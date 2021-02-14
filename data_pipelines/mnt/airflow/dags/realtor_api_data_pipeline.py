from airflow import DAG
from airflow.sensors.http_sensor import HttpSensor
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.slack_operator import SlackAPIPostOperator

from datetime import datetime, timedelta

import csv
import requests
import json
import os


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021, 2, 8),
    'depends_on_false': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'emails': [os.environ['MY_EMAIL']],
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def download_listings(city="Denver", limit='200', page=1):
    '''
    Query Realtor listings API using RapidAPI
    '''
    url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"
    querystring = {"city":city,"limit":limit,"offset":f"{(page-1)*limit}","state_code":"CO","sort":"newest"}
    api_key = os.environ['RAPID_API_REALTOR_APP_KEY']

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "realtor.p.rapidapi.com"
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)

    with open('/usr/local/airflow/dags/files/listings_query.json', 'a') as outfile:
        json.dump(response.json(), outfile)
    

with DAG(dag_id="realtor_api_data_pipeline",
        schedule_interval="0 0 * * *",
        default_args=default_args,
        catchup=False) as dag:

    are_listings_available = HttpSensor(
        task_id='are_listings_available',
        method='GET',
        http_conn_id='forex_api',
        endpoint='properties/v2/list-for-sale/',
        headers={
            'x-rapidapi-key': os.environ['RAPID_API_REALTOR_APP_KEY'],
            'x-rapidapi-host': "realtor.p.rapidapi.com"
        },
        response_check=lambda response: "meta" in response.json().keys(),
        poke_interval=5,
        timeout=20
    )

    downloading_listings = PythonOperator(
        task_id='downloading_listings',
        python_callable=download_listings
    )
    