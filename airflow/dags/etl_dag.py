import os
import sys
import time
import json
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.exceptions import AirflowException
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.mongo.sensors.mongo import MongoSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.apache.hdfs.sensors.hdfs import HdfsSensor
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook
from airflow.providers.apache.hive.hooks.hive import HiveMetastoreHook
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.mongo_to_s3 import MongoToS3Operator
try:
    from extraction.api_extraction import TMDBApiData
except ModuleNotFoundError:
    path = os.path.abspath('.')
    sys.path.insert(1, path)
from extraction.api_extraction import TMDBApiData

date_of_execution = time.strftime("%Y-%m-%d")
print(f'Date of execution: {date_of_execution}')
def get_and_insert_data(mongo_conn_id:str, db:str, collection:str) -> None:
    """
    Función que recibe e inserta cada contenido scrapeado de la API TMDB.
    La inserción se hace via MongoHook, previa validación que el content id
    no esta en la DB.
    Args:
        mongo_conn_id: str
        db: str
        collection: str
    Returns:
        None
    """
    hook = MongoHook(conn_id=mongo_conn_id)
    client = hook.get_conn()
    db = client[db]
    collection = db[collection]
    print(f"Connected to MongoDB - {client.server_info()}")
    data_scraped = list(collection.find({}, {'_id': 0, 'id':1}))
    tmdb_class = TMDBApiData()
    movies = tmdb_class.get_data()
    for movie in movies:
        if any(_dict['id'] == movie['id'] for _dict in data_scraped): continue
        movie['created_at'] = date_of_execution
        collection.insert_one(movie)
        print('Insertado contenido CreatedAt:', movie['created_at'])

def transform_data(mongo_conn_id:str, db:str, collection:str) -> None:
    """
    Función para modificar tipo fields en mongo (string-> dates).
    Utiliza la JSON Query de la carpeta transform y via MongoHook
    hace el update_many.
    Args:
        mongo_conn_id:str
        db: str
        collection:str
    """
    f = open('./transform/set_dates.json')
    query = json.load(f)
    print(query)
    hook = MongoHook(conn_id=mongo_conn_id)
    client = hook.get_conn()
    collection = client[db][collection]
    collection.update_many({'created_at': date_of_execution}, query)
    print('MongoDB data succesfully updated!')
    f.close()

def check_bucket(bucket_name:str, aws_conn_id:str) -> None:
    """
    Función para validar el Bucket en AWS (Minio) via S3Hook.
    Args:
        bucket_name:str
        aws_conn_id:str
    Retuns:
        None
    """
    s3_hook = S3Hook(aws_conn_id)
    bucket_exists = s3_hook.check_for_bucket(bucket_name)
    assert bucket_exists, f'Bucket {bucket_name} not exists! creating...'

def hive_hooks(db:str, table:str, hive_conn:str) -> None:
    """
    Función para validar tabla principal en Hive.
    Si falla el Hook, ejecuta via BashOperator una query de Hive
    para crear la DB y la tabla schema. Si detecta la tabla, se inserta
    datos en la tabal via load_data.hql (parquet to hive).
    Args:
        db:str
        table:str
        hive_conn:str
    Returns:
        None
    """
    hook = HiveMetastoreHook(metastore_conn_id=hive_conn)
    check_table = hook.table_exists(db=db, table_name=table)
    if check_table == False:
        hive_tables_setup = BashOperator(
            task_id='hive_tables_setup',
            bash_command=('docker exec -it hive-server bash -c "hive -f /opt/hive_scripts/create_table.hql"'),
            dag=dag
        )
        hive_tables_setup.execute(context={})
        print('HIVE DATABASE AND TABLE CREATED!')
    else:
        incremental_hive_data = BashOperator(
            task_id='load_data_into_hive',
            bash_command=('docker exec -it hive-server bash -c "hive -f /opt/hive_scripts/load_data.hql"'),
            dag=dag
        )
        incremental_hive_data.execute(context={})
        print('DATA LOADED IN HIVE WAREHOUSE!')
    
default_args = {
                    'owner': 'etl_data_engineer',
                    'reties': 10,
                    'retry_delay': timedelta(minutes=1),
                    'execution_timeout': timedelta(hours=24)
                }
with DAG(
        dag_id='etl_dag_v1',
        start_date=pendulum.yesterday(),
        catchup=False,
        schedule_interval='@daily'
    ) as dag:
        # Group to setup ETL
        with TaskGroup(group_id='etl_verification_group') as etl_setup:
            check_bucket = PythonOperator(
                task_id='check_s3_bucket',
                python_callable=check_bucket,
                op_kwargs={'bucket_name': 'movies-datalake', 
                            'aws_conn_id': 'aws_etl_id'},
                dag=dag
            )
            create_bucket = S3CreateBucketOperator(
                task_id='create_s3_bucket',
                aws_conn_id='aws_etl_id',
                bucket_name='movies-datalake',
                trigger_rule=TriggerRule.ALL_FAILED,
                dag=dag
            )

            check_hdfs_dirs = HdfsSensor(
                task_id='hdfs_dirs_sensor',
                filepath='/user/local-datalake/tmdb/',
                hdfs_conn_id='hdfs_conn_id',
                ignore_copying=True,
                poke_interval=5,
                timeout=30,
                dag=dag
            )
            create_hdfs_dirs = BashOperator(
                    task_id='hdfs_dirs_creation',
                    bash_command='docker exec -it namenode bash "create.sh" || true',
                    trigger_rule=TriggerRule.ALL_FAILED,
                    dag=dag
                )
            empty_operator = EmptyOperator(
                task_id='empty_task',
                trigger_rule=TriggerRule.ALL_DONE,
                dag=dag
            )

            check_bucket >> create_bucket >> empty_operator
            check_hdfs_dirs >> create_hdfs_dirs >> empty_operator

        # Group to get TMDB data via scrapper
        with TaskGroup(group_id='api_scrapper_group') as api_tasks:
            api_task = PythonOperator(
                task_id='tmdb_api_to_local_mongo',
                python_callable=get_and_insert_data,
                op_kwargs={ # Las keys deben coincidir con los parametros de la funcion!! incluso en nombre
                    'mongo_conn_id': 'mongo_etl_id',
                    'db': 'tmdb_data',
                    'collection': 'movies'
                },
                dag=dag
            )

            api_task

        # Group to make Mongo, Minio and Spark operations
        with TaskGroup(group_id='mongo_s3_spark_group') as first_pipeline:
            mongo_sensor_task = MongoSensor(
                task_id='mongo_tmdb_data_sensor',
                collection='movies',
                query={'created_at': date_of_execution},
                mongo_conn_id='mongo_etl_id',
                mongo_db='tmdb_data',
                poke_interval=20,
                timeout=480, 
                dag=dag
            )

            transform_mongo_data = PythonOperator(
                task_id='transform_date_fields',
                python_callable=transform_data,
                op_kwargs={ # Las keys deben coincidir con los parametros de la funcion!! incluso en nombre
                    'mongo_conn_id': 'mongo_etl_id',
                    'db': 'tmdb_data',
                    'collection': 'movies'
                },
                dag=dag
            )

            mongo_to_s3_task = MongoToS3Operator(
                task_id='mongo_to_s3',
                mongo_conn_id='mongo_etl_id',
                aws_conn_id='aws_etl_id',
                mongo_collection='movies',
                mongo_query={},
                mongo_projection={'_id': 0},
                s3_bucket='movies-datalake',
                s3_key='movies.json',
                mongo_db='tmdb_data',
                replace=True,
                allow_disk_use=True,
                dag=dag
            )
        
            s3_sensor_task = S3KeySensor(
                task_id='s3_sensor',
                aws_conn_id='aws_etl_id', 
                bucket_name='movies-datalake',
                bucket_key='movies.json',
                poke_interval=20,
                timeout=480, 
                dag=dag
            )

            spark_task = BashOperator(
                task_id='spark_s3_data_extraction',
                bash_command='docker exec -it spark-master /spark/bin/spark-shell --driver-memory 8G -i /scalafiles/getMinioS3Data.scala',
                dag=dag
            )
            
            mongo_sensor_task >> transform_mongo_data >> mongo_to_s3_task >> s3_sensor_task >> spark_task

        # Group to make HDFS and Hive operations
        with TaskGroup(group_id='hdfs_hive_group') as second_pipeline:
            check_hdfs_parquet_file = HdfsSensor(
                task_id='hdfs_parquet_sensor',
                filepath='/user/local-datalake/tmdb/movies.parquet',
                hdfs_conn_id='hdfs_conn_id',
                ignore_copying=True,
                poke_interval=5,
                timeout=30,
                dag=dag
            )
            
            hive_operations_task = PythonOperator(
                task_id='hive_operations',
                python_callable=hive_hooks,
                op_kwargs={
                            'db': 'warehouse', 
                            'table': 'movies',
                            'hive_conn': 'hive_etl_id'
                        },
                trigger_rule=TriggerRule.ALL_SUCCESS,
                dag=dag
            )

            pyspark_task = BashOperator(
                task_id='pyspark_hive_to_hdfs',
                bash_command='docker exec -it spark-master /spark/bin/spark-submit --driver-memory 8G /pysparkfiles/transform_hive_data.py',
                dag=dag
            )
            
            check_hdfs_parquet_file >> hive_operations_task >> pyspark_task

        etl_setup >> api_tasks >> first_pipeline >> second_pipeline