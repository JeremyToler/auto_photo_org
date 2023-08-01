# TODO Make a nice heading for this code
# TODO Make sure readme file has all instructions for working with the code
# TODO After proccessing files check if there are more than 20 unproccessed images and email/slack me. 

import os
import config
import logging
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from geopy.geocoders import Nominatim

if config.debug_mode:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logging.basicConfig(
    filename='apo.log',
    filemode='w',
    format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s',
    level=loglevel
)
logging = logging.getLogger('APO')

def get_files(unsorted_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(unsorted_path):
        files.extend(filenames)
        # Stop walk from adding filenames in subdirectories.
        break 
    return files

def get_metadata(file_path):
    meta_dict = {}
    gps_tag = 0
    try:
        image = Image.open(file_path)
        exif = image._getexif()
    except:
        return meta_dict
    if not exif:
        return meta_dict
    
    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        logging.debug(f'Metadata Options: Tag = {decoded} Value = {value}')
        if decoded == 'DateTime':
            logging.debug(f'RAW Timestamp from Metadata = {value}')
            meta_dict[decoded] = value
        if decoded == 'GPSInfo':
            gps_tag = tag

    if gps_tag:
        for tag, value in exif[gps_tag].items():
            decoded = GPSTAGS.get(tag, tag)
            meta_dict[decoded] = value
    logging.debug('-------------------GPS TAGS----------------------')
    logging.debug(meta_dict)
    return meta_dict  

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
def process_gps(meta_dict):
    geolocator = Nominatim(user_agent=config.nominatum_agent)
    latitude = convert_gps(*meta_dict['GPSLatitude'], 
                           meta_dict['GPSLatitudeRef'])
    longitude = convert_gps(*meta_dict['GPSLongitude'],
                            meta_dict['GPSLongitudeRef'])
    location = geolocator.reverse(
        f'{latitude}, {longitude}',
        zoom = 10,
        language='en-us'
        )
    city = location.address.split(', ', 1)[0].replace(' ', '_')
    return '.' + re.sub(r'\W', '', city)

'''
Pillow returns GPS coordanats as Degrees, Minutes, Seconds
Nominatim expects GPS coordanats to be Decimal Degrees
'''
def convert_gps(deg, min, sec, ref):
    result = float(deg) + float(min) / 60 + float(sec) / 3600
    if ref in ['W', 'S']:
        result = result * -1
    return result

def get_time(meta_dict, filename):
    if 'DateTime' in meta_dict:
        timestamp = datetime.strptime(meta_dict['DateTime'], f'%Y:%m:%d %H:%M:%S')
        date = timestamp.strftime(f'%Y-%m-%d')
        time = '.' + timestamp.strftime(f'%H%M%S')
    else:
        date, time = time_from_name(filename)
    if 'GPSDateStamp' in meta_dict and time == '':
        timestamp = datetime.strptime(meta_dict['GPSDateStamp'], f'%Y:%m:%d')
        date = timestamp.strftime(f'%Y-%m-%d')
        time = ''
    return [date, time]

'''
Most of the filenames that were made by a camera or phone have the date
in order YYYY MM DD HH MM SS along with other info such as PXL as well
as other formatting. Removing all non digit charecters from the strings
will put them all in the same order and slicing the first 14 get rid of
numbering or miliseconds.
'''
def time_from_name(filename):
    date = time = ''
    stripped = re.sub(r'\D', '', filename.rsplit('.', 1)[0])[:14]
    logging.debug(f'{filename} stripped to {stripped}')
    if not stripped.startswith('20'):
        logging.warning(f'Could not extract time from {filename}')
        logging.debug(f'stripped string does not start with 20')
        return (date, time)
    try:
        logging.debug(f'Stripped Timestamp from filename = {stripped}')
        if len(stripped) == 14:
            timestamp = datetime.strptime(stripped, '%Y%m%d%H%M%S')
            date = timestamp.strftime(f'%Y-%m-%d')
            time = '.' + timestamp.strftime(f'%H%M%S')
        else:
            timestamp = datetime.strptime(stripped[8], '%Y%m%d')
            date = timestamp.strftime(f'%Y-%m-%d')
    except:
        logging.warning(f'Could not extract time from {filename}')
    return (date, time)

def sort_file(old, new):
    i = 0
    new_path = os.path.join(config.sorted_path, new[:4])
    new_file = os.path.join(new_path, new)
    old_file = os.path.join(config.unsorted_path, old)
    if not os.path.exists(config.sorted_path):
        os.mkdir(config.sorted_path)
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    while os.path.isfile(new_file):
        split_name = new_file.rsplit('.', 1)
        new_file = f'{split_name[0]}{i}.{split_name[1]}'
        i += 1
    else:
        os.rename(old_file, new_file)
    logging.info(f'{old_file} has been renamed {new_file}')

def main():
    for filename in get_files(config.unsorted_path):
        logging.debug(f'Proccessing {filename}')
        meta_dict = get_metadata(os.path.join(config.unsorted_path, filename))
        date, time = get_time(meta_dict, filename)
        if date == '': 
            logging.error(f'Cannot get timestamp from {filename}')
            continue
        if 'GPSLatitude' in meta_dict:
            try:
                city = process_gps(meta_dict)
            except:
                ''' 
                Network issues can cause this. 
                Halting renaming this file so it can try again later.
                '''
                logging.exception(f'Unable to proccess GPS for {filename}')
                continue
        else:
            logging.warning(f'{filename} has no GPS Data')
            city = ''
        ext = filename.rsplit('.', 1)[1]
        new_filename = f'{date}{time}{city}.{ext}'
        sort_file(filename, new_filename)

if __name__ == '__main__':
    main()