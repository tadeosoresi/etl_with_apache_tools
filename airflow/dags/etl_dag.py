import os
import sys
import time
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.mongo.sensors.mongo import MongoSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
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
    data_scraped = collection.find({}, {'_id': 0, 'id':1})
    tmdb_class = TMDBApiData()
    tmdb_class.date_of_scraping = date_of_execution
    movies = tmdb_class.get_data()
    for movie in movies:
        if any(_dict['id'] == movie['id'] for _dict in data_scraped): continue
        collection.insert_one(movie)
    hook.close_conn()
 
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

    task1 = PythonOperator(
        task_id='tmdb_api_to_local_mongo',
        python_callable=get_and_insert_data,
        op_kwargs={ # Las keys deben coincidir con los parametros de la funcion!! incluso en nombre
            'mongo_conn_id': 'mongo_etl_id',
            'db': 'tmdb_api',
            'collection': 'movies'
        },
        dag=dag
    )
    task2 = MongoSensor(
        task_id='mongo_tmdb_data_sensor',
        collection='movies',
        query={'created_at': date_of_execution},
        mongo_conn_id='mongo_etl_id',
        mongo_db='tmdb_api',
        poke_interval=20,
        timeout=480, 
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag
    )
    task3 = MongoToS3Operator(
        task_id="mongo_to_s3",
        mongo_conn_id='mongo_etl_id',
        aws_conn_id='aws_etl_id',
        mongo_collection='movies',
        mongo_query={},
        mongo_projection={'_id': 0},
        s3_bucket='movies-datalake',
        s3_key='tmdb_data/',
        mongo_db='tmdb_api',
        replace=True,
        allow_disk_use=True,
        compression='gzip',
        dag=dag
    )
    task1 >> task2 >> task3
    """task1 = S3KeySensor(
        task_id='data_to_minio',
        bucket_name='',
        bucket_key='',
        aws_conn_id='',
        mode='poke',
        poke_interval=5,
        timeout=30
    )
    task2 = MongoToS3Operator(
        mongo_conn_id='',
        aws_conn_id='',
        mongo_collection='',
        mongo_query='',
        s3_bucket='',
        s3_key='',
        mongo_db='',
        replace='',
        allow_disk_use=True,
        compression='gzip'
    )"""