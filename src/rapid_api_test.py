import requests
import os
import pprint

import pymongo
import psycopg2


def listings_query(city="Denver", limit='200'):
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
    return response

def details_query(property_id):
    '''
    Query Realtor details API using RapidAPI, details API
    '''
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"
    querystring = {"property_id":property_id}
    api_key = os.environ['RAPID_API_KEY_REALTOR']

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "realtor.p.rapidapi.com"
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()

class dbConnector():
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        self.mongo_db = self.mongo_client['RealtorStore']

        self.sql_client = psycopg2.connect(
            dbname='realtor_api_listings', user='postgres', password='password',
            host='localhost', port='5432'
        )

    def query_listings(self, city="Denver", limit='200', store_mongo=True):
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

        if store_mongo:
            col = self.mongo_db['listings']
            col.insert_many(response.json())
        
        return response.json()

    def query_details(self, property_id, store_mongo=True):
        '''
        Query Realtor details API using RapidAPI, details API
        '''
        url = "https://realtor.p.rapidapi.com/properties/v2/detail"
        querystring = {"property_id":property_id}
        api_key = os.environ['RAPID_API_KEY_REALTOR']

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "realtor.p.rapidapi.com"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)

        if store_mongo:
            col = self.mongo_db['details']
            col.insert_many(response.json())
        
        return response.json()
    

    def pull_listing(self, one_listing=True):
        col = self.mongo_db['listings']
        query = col.find_one()
        if one_listing:
            return query.get('properties')[0]
        else:
            return query.get('properties')

    def pull_query_meta(self):
        col = self.mongo_db['listings']
        query = col.find_one()
        return query.get('meta')

    def pull_listing_details(self, one_listing=True):
        col = self.mongo_db['details']
        query = col.find_one()
        if one_listing:
            return query.get('properties')[0]
        else:
            return query.get('properties')

    # def to_sql(self):
    #     cur = self.sql_client.cursor()

    

if __name__ == "__main__":
    test_prop_id = 'M1293979562'
    # test = details_query(test_prop_id)


    conn = dbConnector()
    test = conn.pull_listing_details()

    breakpoint()
    # conn.store_details(test)
    # test = importer.pull_query_meta()
    # test = importer.pull_listings()

    pprint.pprint(test)

    

    '''
    Proposed data pipe structure:
     - ping listings API for 200 most recent listings in all 7 metros, weekly - sort search result by date posted
        - Denver, Aurora, Thornton, Littleton, Wesminster, Centennial, Englewood
     - Store in mongo, schema: document = query(dict with fields 'id_', 'meta', 'properties')
     - Pull data from mongo to postgres, in more structured form
     - Weekly, ping details API for listing details
     - store in mongo
     - add in sql table with 'photo_id' as PK
     - dl photos to make dir for ML model
    
    500 requests/mo limit wi/ free account:
     - 4*7 = 28 for metrolistings -> 28*200 -> 5600 properties/mo
     - 472 for details -> 472*20 -> 9440 imgs/mo

    Next Steps:
     - Incorporate pipelines into airflow, webapp
     - Incorporate datavis (tableau)
     - Incorporate style-based, recommender
    '''