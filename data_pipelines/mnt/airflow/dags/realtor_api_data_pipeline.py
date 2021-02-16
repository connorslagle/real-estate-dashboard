from airflow import DAG
from airflow.models import Variable
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

from scripts.aws_helpers import upload_to_s3

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021, 2, 8),
    'depends_on_false': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'emails': [Variable.get('my_email')],
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def download_listings(city="Denver", limit='200', page=1):
    '''
    Query Realtor listings API using RapidAPI
    '''
    url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"
    querystring = {"city":city,"limit":limit,"offset":f"{(page-1)*limit}","state_code":"CO","sort":"newest"}
    api_key = Variable.get('rapid_api_realtor_app_key')

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "realtor.p.rapidapi.com"
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)

    date = datetime.now().date()

    with open(f'/usr/local/airflow/dags/files/listings_query_{str(date)}.json', 'a') as outfile:
        json.dump(response.json(), outfile)

with DAG(dag_id="realtor_api_data_pipeline",
        schedule_interval="0 0 * * *",
        default_args=default_args,
        catchup=False) as dag:

    downloading_listings = PythonOperator(
        task_id='downloading_listings',
        python_callable=download_listings
    )

    saving_listings = BashOperator(
    task_id='saving_listings',
    bash_command="""
        hdfs dfs -mkdir -p /listings && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/listings_query_{}.json /listings
    """.format(str(datetime.now().date()))
    )

    archive_listings_query = PythonOperator(
        task_id='archive_listings_query',
        python_callable=upload_to_s3,
        op_kwargs={
            'fpath':'/usr/local/airflow/dags/files/listings_query_{}.json'.format(str(datetime.now().date())),
            'key':'listings_queries/listings_query_{}.json'.format(str(datetime.now().date())),
            'bucket':'realtor-api-archive'
        }
    )

    creating_listings_table = HiveOperator(
        task_id="creating_listings_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS listings(
                property_id STRING,
                query_date TIMESTAMP,
                query_city STRING,
                query_state STRING,
                prop_type STRING,
                address_line STRING,
                address_city STRING,
                zip_code INT,
                fips_code INT,
                lat DECIMAL(9,6),
                long DECIMAL(9,6),
                neighborhood STRING,
                listing_price DOUBLE,
                baths DOUBLE,
                beds INT,
                building_size INT,
                building_size_units STRING,
                lot_size INT,
                lot_size_units STRING,
                last_update TIMESTAMP,
                url STRING
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    insert_into_listings_table = SparkSubmitOperator(
        task_id='insert_into_listings_table',
        application='/usr/local/airflow/dags/scripts/listings_processing.py',
        conn_id='spark_submit_conn'
    )

