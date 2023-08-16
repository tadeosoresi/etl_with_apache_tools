#!/bin/bash

# to run: sh airflow_and_docker_setup.sh
# important: developed in ubuntu 22.04

# Corta la ejecucion al primer error
set -e

setup_ubuntu() {
    echo 'Updating system, installing Python\n'
    apt-get update && apt-get install -y python3 python3-pip python3-dev python3-venv && apt-get -y install net-tools
    }

up_compose_services() {
    echo 'Launching docker services\n'
    docker compose up -d
    }

up_local_airflow() {

    echo 'Creating virtual environment\n'
    python3 -m venv airflow_env

    echo 'Installing Airflow, setting up Airflow user\n'
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
    }

up_etl_environment
up_compose_services
up_airflow
