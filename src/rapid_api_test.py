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
    return response.json()

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

    def store_listings(self, listing_json):
        col = self.mongo_db['listings']
        col.insert_many(listing_json)
    
    def store_details(self, details_json):
        col = self.mongo_db['details']
        col.insert_many(details_json)

    def pull_listings(self, one_listing=True):
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

    # def to_sql(self):
    #     cur = self.sql_client.cursor()

    

if __name__ == "__main__":
    importer = dbConnector()
    # test = importer.pull_query_meta()
    test = importer.pull_listings()

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

    '''
    SQL Schema
    - Search Table (listing_query)
        - listing_query_id, serial, PK
        - city, varchar(20)
        - state, varchar(2)
        - property_status, varchar(15)
        - query_date, timestamp
        - query_sort, varchar(15)

    CREATE TABLE LISTING_QUERY(
        LISTING_QUERY_ID INT GENERATED ALWAYS AS IDENTITY,
        CITY VARCHAR(20) NOT NULL,
        STATE VARCHAR(2) NOT NULL,
        PROPERTY_STATUS VARCHAR(15) NOT NULL,
        QUERY_DATE TIMESTAMP NOT NULL,
        QUERY_SORT VARCHAR(15) NOT NULL,
        PRIMARY KEY(LISTING_QUERY_ID)
    );

    - Listings Table (listing_data)
        - listing_id, serial, PK
        - query_id, int, FK
        - page, int
        - page_rank, int
        - last_update, timestamp
        - listing_price, int
        - property_type, varchar(20)
        - realtor_listing_id, int
        - mls_id, int
        - property_id, VARCHAR(15)
        - city, varchar(20)
        - state, varchar(2)
        - county, varchar(20)
        - zipcode, int
        - neighborhood, varchar(20)
        - address_line, varchar(30)
        - lat, numeric(8,5)
        - long, numeric(8,5)
        - baths, numeric(3,1)
        - beds, int
        - building_size, int
        - building_units, varchar(10)
        - lot_size, int
        - lot_units, varchar(10)

    CREATE TABLE LISTING(
        LISTING_ID INT GENERATED ALWAYS AS IDENTITY,
        LISTING_QUERY_ID INT NOT NULL,
        PAGE INT NOT NULL,
        PAGE_RANK INT NOT NULL,
        LAST_UPDATE TIMESTAMP NOT NULL,
        LISTING_PRICE INT NOT NULL,
        PROPERTY_TYPE VARCHAR(20) NOT NULL,
        REALTOR_LISTING_ID INT NOT NULL,
        MLS_ID INT NOT NULL,
        PROPERTY_ID VARCHAR(15) NOT NULL,
        CITY VARCHAR(20) NOT NULL,
        STATE VARCHAR(2) NOT NULL,
        COUNTY VARCHAR(20) NOT NULL,
        ZIPCODE INT NOT NULL,
        NEIGHBORHOOD VARCHAR(20) NOT NULL,
        ADDRESS_LINE VARCHAR(30) NOT NULL,
        LAT NUMERIC(8,5) NOT NULL,
        LONG NUMERIC(8,5) NOT NULL,
        BATHS NUMERIC(3,1) NOT NULL,
        BEDS INT NOT NULL,
        BUILDING_SIZE INT NOT NULL,
        BUILDING_UNITS VARCHAR(10) NOT NULL,
        LOT_SIZE INT NOT NULL,
        LOT_UNITS VARCHAR(10) NOT NULL,
        PRIMARY KEY(LISTING_ID),
        CONSTRAINT FK_QUERY
            FOREIGN KEY(LISTING_QUERY_ID)
                REFERENCES LISTING_QUERY(LISTING_QUERY_ID)
    );

    - details query
        - 


    - Photo Table (listing_images)
        - photo_id, serial, PK
        - query_id, int, FK
        - listing_id, int, FK
        - photo_url, varchar(50)
        - S3_location, varchar(50)
        - (from detailsAPI query)

    CREATE TABLE IMAGES(
        IMAGE_ID INT GENERATED ALWAYS AS IDENTITY,
        QUERY_ID INT NOT NULL,
        LISTING_ID INT NOT NULL,
        IMAGE_URL VARCHAR(100)
        PRIMARY KEY(IMAGE_ID),
        CONSTRAINT FK_QUERY
            FOREIGN KEY(QUERY_ID)
                REFERENCES QUERY(QUERY_ID)
    );
    '''