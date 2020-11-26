import requests
import os
import pprint

def listings_query(city="Denver", limit='200'):
    '''
    Query Realtor API using RapidAPI
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
    Query Realtor API using RapidAPI, details API
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

if __name__ == "__main__":
    prop_id = test.get('properties')[0].get('property_id')

    detail_query = {"property_id":prop_id}
    detail_url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    detail_response = requests.request("GET", detail_url, headers=headers, params=detail_query)
    details = detail_response.json()
    pprint.pprint(details)

    '''
    Wednesday November 25, 2020: Can access photos using deatils api. Will need to test if I can dl.
    '''