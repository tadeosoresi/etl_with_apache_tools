#!/bin/bash
export AIRFLOW_HOME=${PWD}
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW_FIRSTNAME=Peter
export AIRFLOW_LASTNAME=Parker
export AIRFLOW_USER=admin
export AIRFLOW_PASSWORD=admin
export AIRFLOW_EMAIL=example@gmail.com
export POSTGRES_USER=etlDataEngineer
export POSTGRES_PASSWORD=etlPassword
export POSTGRES_DB=local_airflow_db
export AIRFLOW_POSTGRES_CONN='postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5444/${POSTGRES_DB}'