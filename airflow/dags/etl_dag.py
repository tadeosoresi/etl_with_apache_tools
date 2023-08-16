import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.providers.amazon.aws.transfers.mongo_to_s3 import MongoToS3Operator

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
    task1 = S3KeySensor(
        task_id='data_to_minio',
        bucket_name='',
        bucket_key='',
        aws_conn_id='',
        mode='poke',
        poke_interval=5,
        timeout=30
    )