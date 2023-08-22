#!/bin/bash

# to run: sudo sh airflow_and_docker_setup.sh
# important: developed in ubuntu 22.04, must execute in super user mood

# Verificar si el script se está ejecutando como root
if [ "$EUID" -ne 0 ]
  then echo "Script must be execute in super user (sudo) mood"
  exit
fi

# Corta la ejecucion al primer error
set -e

setup_ubuntu() {
    echo '\nUpdating system, installing Python\n'
    apt-get update && apt-get install -y python3 python3-pip python3-dev python3-venv && apt-get -y install net-tools
    }

up_compose_services() {
    echo '\nLaunching docker services\n'
    docker compose up -d
    }

up_local_airflow() {

    echo '\nCreating virtual environment\n'
    python3 -m venv airflow_env

    echo '\nInstalling Airflow, setting up Airflow user\n'
    . airflow_env/bin/activate && pip3 install --upgrade pip && \
    pip3 install 'apache-airflow[amazon]==2.4.2' \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.4.2/constraints-3.8.txt" && \
    pip3 install -r requirements.txt
    }

setup_ubuntu
up_compose_services
up_local_airflow
