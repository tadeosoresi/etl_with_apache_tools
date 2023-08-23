#!/bin/bash
export AIRFLOW_HOME=${PWD}
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW_FIRSTNAME=Peter
export AIRFLOW_LASTNAME=Parker
export AIRFLOW_USER=etlDataEngineer
export AIRFLOW_PASSWORD=etlPassword
export AIRFLOW_EMAIL=example@gmail.com
export POSTGRES_USER=etlDataEngineer
export POSTGRES_PASSWORD=etl1234
export POSTGRES_DB=etl_database
export SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5444/${POSTGRES_DB}
export TMDB_API_TOKEN=''
export AIRFLOW_CONN_MONGO_DEFAULT='mongo://ETLDataEngineer:ETLDataEngineerPassword@localhost:27018'
# to run: source environment_variables.sh