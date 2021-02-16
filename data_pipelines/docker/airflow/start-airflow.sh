#!/usr/bin/env bash

# Create the user airflow in the HDFS
hdfs dfs -mkdir -p    /user/airflow/
hdfs dfs -chmod g+w   /user/airflow

# Move to the AIRFLOW HOME directory
cd $AIRFLOW_HOME

# add env api keys to container bashrc
cat .bashrc_for_airflow >> .bashrc
source .bashrc

# add env api keys to profile as well, might be needed for webserver
cat .bashrc_for_airflow >> .profile
source .profile

# Initiliase the metadatabase
airflow initdb

# Run the scheduler in background
airflow scheduler &> /dev/null &

# Run the web sever in foreground (for docker logs)
exec airflow webserver