import boto3

def upload_to_s3(fpath, key, bucket):
    '''
    Uploads json to s3 for archiving.
    '''
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).upload_file(fpath, key)

if __name__=='__main__':
    upload_to_s3(
        '../files/listings_query_2021-02-15.json',
        'listings_queries/listings_query_2021-02-15.json',
        'realtor-api-archive'
        )
    