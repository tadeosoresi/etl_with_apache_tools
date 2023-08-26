import os
import sys
import time
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.mongo.sensors.mongo import MongoSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
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
def get_and_insert_data(mongo_conn_id, db, collection):
    """
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

def check_bucket(bucket_name, aws_conn_id):
    """
    """
    s3_hook = S3Hook(aws_conn_id)
    bucket_exists = s3_hook.check_for_bucket(bucket_name)
    assert bucket_exists, f'Bucket {bucket_name} not exists! creating...'

default_args = {
                    'owner': 'etl_data_engineer',
                    'reties': 10,
                    'retry_delay': timedelta(minutes=2)
                }
with DAG(
        dag_id='etl_dag_v1',
        start_date=pendulum.yesterday(),
        schedule_interval='@daily'
) as dag:

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
    task1 = PythonOperator(
        task_id='tmdb_api_to_local_mongo',
        python_callable=get_and_insert_data,
        op_kwargs={ # Las keys deben coincidir con los parametros de la funcion!! incluso en nombre
            'mongo_conn_id': 'mongo_etl_id',
            'db': 'tmdb_data',
            'collection': 'movies'
        },
        dag=dag
    )
    task2 = MongoSensor(
        task_id='mongo_tmdb_data_sensor',
        collection='movies',
        query={'created_at': date_of_execution},
        mongo_conn_id='mongo_etl_id',
        mongo_db='tmdb_data',
        poke_interval=20,
        timeout=480, 
        dag=dag
    )
    task3 = MongoToS3Operator(
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
    task4 = S3KeySensor(
        task_id='s3_sensor',
        aws_conn_id='aws_etl_id', 
        bucket_name='movies-datalake',
        bucket_key='movies.json',
        poke_interval=20,
        timeout=480, 
        dag=dag
    )
    task5 = BashOperator(
        task_id='s3_data_extraction',
        bash_command='docker exec -it spark-master /spark/bin/spark-shell -i /scalafiles/getMinioS3Data.scala',
        dag=dag
    )

    check_bucket >> create_bucket
    task1 >> task2 >> task3 >> task4