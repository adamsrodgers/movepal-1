'''
In main, only use the for_sale_list function within this file. the reason is because this function //

To see the sequence of function calls, use this link: https://drive.google.com/file/d/1FxhwhzhHELXZlVXALHNk3btchfJ48Hkw/view?usp=sharing
'''

import requests
import json
from os import system, popen
from api_output import for_sale_list_data, attom_data
from sqlalchemy import create_engine

#querystring args: offset(unnecessary),limit(set to 10),sort,state_code,city,price_min,price_max,beds_min,beds_max,baths_min,baths_max,hoa_max

#querystring = {"offset":"0","limit":"42","state_code":"OR","city":"Milwaukie","sort":"newest"}

def for_sale_list(querystring):#querystring gets passed as an argument in order to give the users more options
    url = "https://us-real-estate.p.rapidapi.com/for-sale"
    headers = {
        'x-rapidapi-key': "2b7e480369msh22f638972742999p193665jsnfebed1d6da16",
        'x-rapidapi-host': "us-real-estate.p.rapidapi.com"
    }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    parsed_house_list = parse_for_sale_list(response.json()) #this parses the data and passes it off to get_attom_data
    return parsed_house_list

#print(for_sale_list(querystring))

#interesting attom calls below
#/property/detail   -> in property extended
#/schools/snapshot  -> to get schools within 5 miles of latitude and longitude
#/school/detail   -> to get details of the schools listed in /schools/snapshot

def parse_for_sale_list(data):
    array_of_houses=[]
    house={}
    id=0
    for address in data["data"]["results"]:
        pictures=[]#makes sure pictures is empty in order to add photo links
        house["address"] = permalink_to_atom_address(address["permalink"])#this address will then be used by the attom api
        for photo in address["photos"]:
            pictures.append(photo["href"])#adds the photos of the house to the dictionary
        house["photos"] = pictures.copy()
        #print(house["photos"])
        #house["street_view"] = address["location"]["street_view_url"] #maybe for a future update
        #print(address["location"]["address"])
        try:
            house["latitude"] = address["location"]["address"]["coordinate"]["lat"] 
            house["longitude"] = address["location"]["address"]["coordinate"]["lon"]
        except Exception as e:
            print(e)
            house["latitude"]="none"
            house["longitude"]="none"
        house["county"] = address["location"]["county"]["name"]
        house["list_price"] = address["list_price"]
        house["list_date"] = address["list_date"]
        house["description"] = {}
        house["description"]["year_built"] = address["description"]["year_built"]
        house["description"]["lot_sqft"] = address["description"]["lot_sqft"]
        house["description"]["house_sqft"] = address["description"]["sqft"]
        house["description"]["number_of_bathrooms"] = address["description"]["baths"]
        house["description"]["number_of_garages"] = address["description"]["garage"]
        house["description"]["number_of_bedrooms"] = address["description"]["beds"]
        house["description"]["stories"] = address["description"]["stories"]
        house["movepal_id"]=id
        id += 1
        array_of_houses.append(house.copy())
    return array_of_houses

def get_attom_data(parsed_house):#add more data to parsed_house from the attom api
    if(parsed_house["latitude"] == "none"):#error checking
        parsed_house["school_data"]=[]
        return parsed_house
    
    attom_data=[]#this is where all the data from the attom api gets stored and gets used
    parsed_school={}
    attom_api_key='f1465f8900392e45680866cd40d4f199'    #'806dc22c9ef6ad5c06d8639c94192e27'    #'2b1e86b638620bf2404521e6e9e1b19e'
    attom_headers={
        'apiKey': attom_api_key
    }
    curl_link="curl -X GET --header 'Accept: application/json' --header 'apikey: f1465f8900392e45680866cd40d4f199' --header 'accept: application/json' 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/school/snapshot?latitude="+str(parsed_house["latitude"])+"&longitude="+str(parsed_house["longitude"])+"'"

    schools_list=popen(curl_link).read()
    schools_list_json=json.loads(schools_list)
    
    number_of_schools=len(schools_list_json["school"])
    counter=0
    #for school in schools_list_json["school"]:
    while(counter<3 and counter<number_of_schools):#this is to avoid too many api calls
        school=schools_list_json["school"][counter]
        parsed_school["id"]=school["Identifier"]["OBInstID"]
        parsed_school["name"]=school["School"]["InstitutionName"]
        parsed_school["min_grade"]=school["School"]["gradelevel1lotext"]
        parsed_school["max_grade"]=school["School"]["gradelevel1hitext"]
        parsed_school["type"]=school["School"]["Filetypetext"] #public or private
        parsed_school["address"]=school["School"]["locationaddress"]
        parsed_school["distance_from_house"]=str(school["School"]["distance"])+" miles"
        #From here, we use the id in order to find details about the specific school
        curl_link="curl -X GET --header 'Accept: application/json' --header 'apikey: f1465f8900392e45680866cd40d4f199' 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/school/detail?id="+str(parsed_school["id"])+"'"
        school_detail=popen(curl_link).read()
        school_detail_json=json.loads(school_detail)
        parsed_school["district_name"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolLocation"]["districtname"]
        parsed_school["school_webpage"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolContact"]["Websiteurl"]
        #parsed_school["collegebound_percent"]=school_detail_json["school"][0]["SchoolDetail"]["collegebound"] #commented out because this only applies to high schools
        parsed_school["poverty_percent"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolDetail"]["Povertylevel"]
        
        #print(parsed_school)
        attom_data.append(parsed_school.copy())
        
        counter += 1
    parsed_house["school_data"]=attom_data
    return parsed_house


def permalink_to_atom_address(addr):#this function properly formats the permalink to an appropriate data
    newaddr=''
    length=len(addr)
    i=0
    initial=0
    
    while i < length:
        if addr[i]=='-':
            newaddr += ' '
        elif addr[i]=='_':
            if initial<3:
                newaddr += ', '
                initial += 1
            else:
                #remove the remaining
                break
        else:
            newaddr += addr[i]
        i += 1
    return newaddr

def save_house():
    #dataframe to save houses to database
    #if user clicks on "like" for a house, add to saved_houses
    
    array_of_houses=[] #using the parse_for_sale_list() method to get the data from the results
    house={}
    id=0
    for address in data["data"]["results"]:
        pictures=[]#makes sure pictures is empty in order to add photo links
        house["address"] = permalink_to_atom_address(address["permalink"])#this address will then be used by the attom api
        for photo in address["photos"]:
            pictures.append(photo["href"])#adds the photos of the house to the dictionary
        house["photos"] = pictures.copy()
        #print(house["photos"])
        #house["street_view"] = address["location"]["street_view_url"] #maybe for a future update
        #print(address["location"]["address"])
        try:
            house["latitude"] = address["location"]["address"]["coordinate"]["lat"] 
            house["longitude"] = address["location"]["address"]["coordinate"]["lon"]
        except Exception as e:
            print(e)
            house["latitude"]="none"
            house["longitude"]="none"
        house["county"] = address["location"]["county"]["name"]
        house["list_price"] = address["list_price"]
        house["list_date"] = address["list_date"]
        house["description"] = {}
        house["description"]["year_built"] = address["description"]["year_built"]
        house["description"]["lot_sqft"] = address["description"]["lot_sqft"]
        house["description"]["house_sqft"] = address["description"]["sqft"]
        house["description"]["number_of_bathrooms"] = address["description"]["baths"]
        house["description"]["number_of_garages"] = address["description"]["garage"]
        house["description"]["number_of_bedrooms"] = address["description"]["beds"]
        house["description"]["stories"] = address["description"]["stories"]
        house["movepal_id"]=id
        id += 1
        array_of_houses.append(house.copy())
        saved_houses = []
        #what i want is to loop only through the house that the user wants to save, 
        #and then copy the data that we are getting then place this into a dataframe to save to database based on username to display in saved page
        for houses in array_of_houses: 
            photos = house['photos']
            address = house['address']
            year_built = address["description"]["year_built"]
            county_name = address["location"]["county"]["name"]
            list_price = address["list_price"]
            list_date = address["list_date"]
            prop_sqft = address["description"]["lot_sqft"]
            total_sqft = address["description"]["sqft"]
            number_of_bathrooms = address["description"]["baths"]
            num_of_garages = address["description"]["garage"]
            number_of_bedrooms = address["description"]["beds"]
            stories = address["description"]["stories"]
            saved_houses.append([photos, address, year_built, county_name, list_price, list_date, prop_sqft, total_sqft, number_of_bedrooms, num_of_garages, number_of_bedrooms, stories])
            

    
    col_names = ['photos', 'address','year_built', 'list_price', 'list_date', 'county_name', 'number_of_bedrooms', 'number_of_bathrooms', 'prop_sqft','total_sqft' ,'num_of_garages', 'stories']
    df = pd.DataFrame(saved_houses, columns = col_names)
    engine = create_engine('mysql://root:codio@localhost/save_houses')
    df.to_sql('saved_house', con=engine, if_exists='replace', index=False)
    
    #df = df.append(dict(zip(df.col_names, array_of_houses)), ignore_index=True) 
    
    

'''
test=for_sale_list_data
x=parse_for_sale_list(test)
print("/n/n",x,"/n/n")
y=get_attom_data(x[12])
print("\n\n",y,"\n\n")
'''