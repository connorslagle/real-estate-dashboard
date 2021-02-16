import boto3
import os
from airflow.models import Variable



def upload_to_s3(fpath, key, bucket):
    '''
    Uploads json to s3 for archiving.
    '''

    s3 = boto3.client(
        's3',
        aws_access_key_id=Variable.get('aws_access_key_id'),
        aws_secret_access_key=Variable.get('aws_secret_access_key')
    )

    s3.upload_file(fpath, bucket, key)

if __name__=='__main__':
    # upload_to_s3(
    #     '../files/listings_query_2021-02-15.json',
    #     'listings_queries/listings_query_2021-02-15.json',
    #     'realtor-api-archive'
    #     )
    pass
