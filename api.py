import requests

zillow_api_key=''
zillow_link='https://rentalsapi.zillowgroup.com/listings/v1/listingsForUser?apiKey='+zillow_api_key

def get_zillow_data():
    pass

def parse_zillow_data():
    pass

data= requests.get('https://rentalsapi.zillowgroup.com/listings/v1/listingsForUser', apiKey='')
print(data.json())