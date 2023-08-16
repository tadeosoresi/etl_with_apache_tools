#!/bin/bash
echo 'Updating system, installing Python'
apt-get update && apt-get install -y python3-pip python3-dev python3-venv && apt-get -y install net-tools

echo 'Creating virtual environment'
python3 -m venv airflow_env
echo 'Installing Airflow, setting up Airflow user'
python3 . airflow_env/bin/activate && pip3 install --upgrade pip && \
pip3 install 'apache-airflow[amazon]==2.4.2' \
--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.4.2/constraints-3.8.txt" && \
pip3 install -r requirements.txt && airflow db init && airflow users create \
                                                                    --username ${AIRFLOW_USER} \
                                                                    --password ${AIRFLOW_PASSWORD} \
                                                                    --firstname ${AIRFLOW_FIRSTNAME} \
                                                                    --lastname ${AIRFLOW_LASTNAME} \
                                                                    --role Admin \
                                                                    --email ${AIRFLOW_EMAIL}
echo 'Launching docker services'
docker compose up -d
echo 'ETL is UP! :)'

# to run: sh airflow_and_docker_setup.sh
# important: developed in ubuntu 22.04

