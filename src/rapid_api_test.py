import requests
import os
import pprint
import pymongo

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

class mongoImporter():
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        self.mongo_db = self.mongo_client['RealtorStore']

    def store_listings(self, listing_json):
        col = self.mongo_db['listings']
        col.insert_many(listing_json)
    
    def store_details(self, details_json):
        col = self.mongo_db['details']
        col.insert_many(details_json)
    

if __name__ == "__main__":
    # prop_id = test.get('properties')[0].get('property_id')

    '''
    Wednesday November 25, 2020: Can access photos using deatils api. Will need to test if I can dl.
    '''
    listing_json = listings_query()

    importer = mongoImporter()
    importer.store_listings(listing_json)
