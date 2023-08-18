import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.providers.amazon.aws.transfers.mongo_to_s3 import MongoToS3Operator
try:
    from extraction.api_extraction import TMDBApiData
except ModuleNotFoundError:
    path = os.path.abspath('.')
    sys.path.insert(1, path)
from extraction.api_extraction import TMDBApiData

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
        task_id='tmdb_api_data',
        python_callable=TMDBApiData.get_data,
        dag=dag
    )
    task1
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