
try:
    import seiscomp3.Logging as logging
except:
    import logging 

import requests
import json
import os
import configparser


config_path = os.path.join(os.environ['SEISCOMP_ROOT'],'share/gds/tools/', 'config_utilities.cfg')


if not config_path:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_utilities.cfg')

def read_config_file(json_file_path):
    """
    Reads a json_file and returns it as a python dict
    
    :param string json_file_path: path to a json file with configuration information
    :returns: dict
    """
    
    json_file=check_file(json_file_path)
    with open(json_file) as json_data:
        return json.load(json_data)
    

def read_parameters(file_path):
    """
    Read a configuration text file
    
    :param string file_path: path to configuration text file
    :returns: dict: dict of a parser object
    """
    parameter_file=check_file(file_path)
    parser=configparser.ConfigParser()
    parser.read(parameter_file)    
    return parser._sections


def check_file(file_path):
    '''
    Check if the file exists
    
    :param string file_path: path to file to check
    :return: file_path
    :raises Exception e: General exception if file doesn't exist. 
    '''
    try:
        
        with open(file_path):
            return file_path

    except Exception as e:
        logging.error("Error in check_file(%s). Error: %s " %(file_path,str(e)))
        raise Exception("Error in check_file(%s). Error: %s " %(file_path,str(e)))







def short_url(long_url):

    cfg = read_parameters(config_path)
    endpoint = 'https://api-ssl.bitly.com/v4/shorten'
    key = cfg['ig_info']['bitly_key']
    group_id = cfg['ig_info']['bitly_group_id']

    header = {  "Authorization": "%s" %key,
                "Content-Type" : "application/json",
            }
    #params = { "long_url" : long_url, "domain": "bit.ly", "group_guid": group_id } 
    params = { "long_url" : long_url} 

    try:
        response = requests.post(endpoint, headers=header,json=params)
        data = response.json()

        if not response.ok:
            logging.error("Error in utilities.short_url: %s %s" %(response, data))
            print("Error in utilities.short_url: %s %s" %(response, data))
            return "---"
        return data['link']

    except Exception as e:
        print("Error in short_url: error: %s response:%s data:%s" %(str(e),response,data))
        logging.error("Error in short_url: error: %s response:%s data:%s" %(str(e),response,data))
        return "---"


def get_closest_city(latitude,longitude):

    cfg = read_parameters(config_path)
    try:
        query = '%s/get_nearest_city?lat=%s&lon=%s&token=%s'%(cfg['ig_info']['geolocation_service_url'],latitude,longitude,cfg['ig_info']['geolocation_service_token'])
        result = requests.get(query)
        #distance,city,province = result.text.strip('()').encode('utf-8',errors='ignore').split(',')
        distance,city,province = result.text.strip('()').split(',')
        return 'a %s km de %s, %s' %(distance,city.strip(" '"),province.strip(" '"))
    except Exception as e:
        msg_error = "##Error in get_closest_city:%s %s " %(str(e),result.text)
        logging.error(msg_error)
        return '--'

def get_survey_url(local_time,event_id):
    
    cfg = read_parameters(config_path)
    date_event = local_time.strftime("%Y-%m-%d")
    time_event = local_time.strftime("%H:%M:%S")
    if cfg['ig_info']['survey_type'] == "arcgis":
        return short_url(cfg['ig_info']['arcgis_survey_url'] %(event_id,date_event,time_event))
    else:
        return short_url(cfg['ig_info']['google_survey_url'] %(event_id, date_event, time_event))

def get_message_by_country(latitud,longitud):

    cfg = read_parameters(config_path)
    try:
        query = '%s/get_country?lat=%s&lon=%s&token=%s'%(cfg['ig_info']['geolocation_service_url'],latitud,longitud,cfg['ig_info']['geolocation_service_token'])
        result = requests.get(query)
        country = result.text
        country_text = "Ecuador"

        if country == 'Ecuador':
            return country_text
        elif country == 'Colombia':
            country_text = "\nFuente oficial COLOMBIA: \nhttps://www.sgc.gov.co/sismos \nhttps://twitter.com/sgcol"
        elif country == 'Peru':
            country_text = "\nFuente oficial PERU: \nhttps://www.gob.pe/igp \nhttps://twitter.com/Sismos_Peru_IGP"
        else:
            country_text = "\nOtras fuentes que pueden consultarse:\nhttps://www.emsc-csem.org/#2\nhttps://earthquake.usgs.gov/earthquakes/map/\nhttps://geofon.gfz-potsdam.de/eqinfo/list.php"

        return country_text     

    except Exception as e: 
        msg_error = "##Error in get_country:%s" %str(e)
        logging.error(msg_error)
        return '---'


def get_message_by_country_twitter(latitud,longitud):

    cfg = read_parameters(config_path)
    try:
        query = '%s/get_country?lat=%s&lon=%s&token=%s'%(cfg['ig_info']['geolocation_service_url'],latitud,longitud,cfg['ig_info']['geolocation_service_token'])
        result = requests.get(query)
        country = result.text
        country_text = "Ecuador"

        if country == 'Ecuador':
            return country_text
        elif country == 'Colombia':
            country_text = "\nFuente oficial COLOMBIA: https://www.sgc.gov.co/sismos"
        elif country == 'Peru':
            country_text = "\nFuente oficial PERU: https://www.gob.pe/igp"
        else:
            country_text = "\nFuente internacional:https://earthquake.usgs.gov/earthquakes/map/"

        return country_text  
    
    except Exception as e: 
        msg_error = "##Error in get_country_twitter:%s" %str(e)
        logging.error(msg_error)
        return '---'


