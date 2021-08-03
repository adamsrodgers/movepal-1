'''
In main, only use the for_sale_list function within this file. the reason is because this function //

To see the sequence of function calls, use this link: https://drive.google.com/file/d/1FxhwhzhHELXZlVXALHNk3btchfJ48Hkw/view?usp=sharing
'''

import requests
import json
from os import system, popen
from api_output import for_sale_list_data, attom_data
'''

#querystring args: offset(unnecessary),limit(can be fixed),sort,state_code,city,price_min,price_max,beds_min,beds_max,baths_min,baths_max,hoa_max

querystring = {"offset":"0","limit":"42","state_code":"OR","city":"Milwaukie","sort":"newest"}

def for_sale_list(querystring):#querystring gets passed as an argument in order to give the users more options
    url = "https://us-real-estate.p.rapidapi.com/for-sale"
    headers = {
        'x-rapidapi-key': "2b7e480369msh22f638972742999p193665jsnfebed1d6da16",
        'x-rapidapi-host': "us-real-estate.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    parsed_house_list = parse_for_sale_list(response.json()) #this parses the data and passes it off to get_attom_data

#print(for_sale_list(querystring))
'''
#interesting attom calls below
#/property/detail   -> in property extended
#/schools/snapshot  -> to get schools within 5 miles of latitude and longitude
#/school/detail   -> to get details of the schools listed in /schools/snapshot

def parse_for_sale_list(data):
    array_of_houses=[]
    house={}
    for address in data["data"]["results"]:
        pictures=[]#makes sure pictures is empty in order to add photo links
        house["address"] = permalink_to_atom_address(address["permalink"])#this address will then be used by the attom api
        for photo in address["photos"]:
            pictures.append(photo["href"])#adds the photos of the house to the dictionary
        house["photos"] = pictures.copy()
        #house["street_view"] = address["location"]["street_view_url"] #maybe for a future update
        house["latitude"] = address["location"]["address"]["coordinate"]["lat"] 
        house["longitude"] = address["location"]["address"]["coordinate"]["lon"]
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
        array_of_houses.append(house.copy())
    for match in array_of_houses:
        match=get_attom_data(match)########################################################################################################################################

    print(array_of_houses)
    return array_of_houses

def get_attom_data(parsed_house):#add more data to parsed_house from the attom api
    attom_data=[]#this is where all the data from the attom api gets stored and gets used
    parsed_school={}
    attom_api_key='806dc22c9ef6ad5c06d8639c94192e27'    #'2b1e86b638620bf2404521e6e9e1b19e'
    attom_headers={
        'apiKey': attom_api_key
    }
    curl_link="curl -X GET --header 'Accept: application/json' --header 'apikey: 806dc22c9ef6ad5c06d8639c94192e27' --header 'accept: application/json' 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/school/snapshot?latitude="+str(parsed_house["latitude"])+"&longitude="+str(parsed_house["longitude"])+"'"
    #print(curl_link)
    #the reason popen is used instead of requests.get is because the json file being returned has a null value which python can't interpret
    #schools_list=popen("curl -X GET --header 'Accept: application/json' --header 'apikey: 806dc22c9ef6ad5c06d8639c94192e27' --header 'accept: application/json' 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/school/snapshot?latitude=45.442865&longitude=-122.584069'").read()
    schools_list=popen(curl_link).read()
    #print("THIS IS THE SCHOOLS LISTTTT:  ", schools_list,'\n\n')
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
        curl_link="curl -X GET --header 'Accept: application/json' --header 'apikey: 806dc22c9ef6ad5c06d8639c94192e27' 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/school/detail?id="+str(parsed_school["id"])+"'"
        school_detail=popen(curl_link).read()
        school_detail_json=json.loads(school_detail)
        parsed_school["district_name"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolLocation"]["districtname"]
        parsed_school["school_webpage"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolContact"]["Websiteurl"]
        #parsed_school["collegebound_percent"]=school_detail_json["school"][0]["SchoolDetail"]["collegebound"] #commented out because this only applies to high schools
        parsed_school["poverty_percent"]=school_detail_json["school"][0]["SchoolProfileAndDistrictInfo"]["SchoolDetail"]["Povertylevel"]
        
        print(parsed_school)
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



test='7016-SE-Plum-Dr_Milwaukie_OR_97222_M14730-94081'
y={
    "address":permalink_to_atom_address(test),
    "latitude": 45.442865,
    "longitude": -122.584069
}
x=get_attom_data(y)#this works
print(x)



#permalink_to_atom_address(test)
#print(parse_for_sale_list(for_sale_list_data))

#the following code is for testing purposes


'''
parsed_house_list=parse_for_sale_list(for_sale_list_data)
number_of_houses=len(parsed_house_list)
i=0
while i<number_of_houses:
    parsed_house_list[i]=get_attom_data(parsed_house_list[i])
    i += 1
    
print(parsed_house_list)
'''
