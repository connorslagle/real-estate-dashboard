from __future__ import print_function

import time
from builtins import range
from pprint import pprint
import requests
import os

# general airflow
from airflow.utils.dates import days_ago
from airflow.models import DAG
from airflow.exceptions import AirflowException

# airflow operators
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.operators.python_operator import PythonOperator

# hook for AWS DynamoDB
from airflow.contrib.hooks.aws_hook import AwsHook


args = {
    'owner': 'Airflow',
    'start_date': days_ago(2),
}

dag = DAG(
    dag_id='weekly_metro_listings_pull',
    default_args=args,
    schedule_interval=None,
    tags=['Realtor_API','Denver Metro']
)

sensor = HttpSensor(
    task_id='http_sensor_check',
    http_conn_id='https://realtor.p.rapidapi.com/',
    endpoint='properties/v2/list-for-sale',
    request_params={},
    response_check=lambda response: "meta" in response.json().keys(),
    poke_interval=5,
    dag=dag,
)

# [START listings_api query]
t1 = SimpleHttpOperator(
    task_id='listings_query',
    method='GET',
    endpoint=
    python_callable=print_context,
    dag=dag,
)

t2 = SimpleHttpOperator(
    task_id='get_op',
    method='GET',
    endpoint='get',
    data={"param1": "value1", "param2": "value2"},
    headers={},
    dag=dag,
)
# [END listings_api_query]


# [START howto_operator_python_kwargs]
def listings_query(city, limit):
    '''
    Query Realtor listings API using RapidAPI
    '''
    url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"
    querystring = {"city":city,"limit":limit,"offset":"0","state_code":"CO","sort":"relevance"}
    api_key = os.environ['RAPID_API_KEY_REALTOR']

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "realtor.p.rapidapi.com"
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)


    return response.json()


# Generate 5 sleeping tasks, sleeping from 0.0 to 0.4 seconds respectively
cities = ["Denver", "Aurora", "Boulder"]
for city in cities:
    task = PythonOperator(
        task_id='listings_api_' + city + "_200",
        python_callable=listings_query,
        op_kwargs={'city': city, 'limit':"200"},
        dag=dag,
    )

    run_this >> task
# [END howto_operator_python_kwargs]
