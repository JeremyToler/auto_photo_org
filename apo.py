'''
    PAVONINE - Photo And Video Organizer
'''
# TODO Add video support
# TODO Test mp4
# TODO Test avi
# TODO Test mkv
# TODO Test very old video
# TODO Make a nice heading for this code
# pip install pillow, geopy
# TODO How do I make a requirements file?
# TODO Make sure readme file has all instructions for working with the code

import os
import config
import logging
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
        # TODO Change of plans, lets include subdirectories. 
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
        if decoded == 'DateTime':
            meta_dict[decoded] = value
        if decoded == 'GPSInfo':
            gps_tag = tag

    if gps_tag:
        for tag, value in exif[gps_tag].items():
            decoded = GPSTAGS.get(tag, tag)
            meta_dict[decoded] = value
    return meta_dict  

# Converts time from '2023:01:15 18:25:07' to '2023-01-15.182507.'
def process_timestamp(timestamp):
    date_object = datetime.strptime(timestamp, f'%Y:%m:%d %H:%M:%S')
    date = date_object.strftime(f'%Y-%m-%d')
    time = date_object.strftime(f'%H%M%S')
    return {'date': date, 'time': time}

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
    city = location.address.split(', ', 1)[0]
    return '.' + city.replace(' ', '_')

'''
Pillow returns GPS coordanats as Degrees, Minutes, Seconds
Nominatim expects GPS coordanats to be Decimal Degrees
'''
def convert_gps(deg, min, sec, ref):
    result = float(deg) + float(min) / 60 + float(sec) / 3600
    if ref in ['W', 'S']:
        result = result * -1
    return result

def sort_file(old, new):
    new_path = os.path.join(config.sorted_path, new[:4])
    new_file = os.path.join(new_path, new)
    old_file = os.path.join(config.unsorted_path, old)
    if not os.path.exists(config.sorted_path):
        os.mkdir(config.sorted_path)
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    os.rename(old_file, new_file)
    logging.info(f'{old_file} has been renamed {new_file}')

def main():
    # Numbering files so that no 2 files will have the same name
    i = 0 
    for filename in get_files(config.unsorted_path):
        logging.debug(f'Proccessing {filename}')
        meta_dict = get_metadata(os.path.join(config.unsorted_path, filename))

        # TODO Move this error checking to its own function.
        if not meta_dict: 
            logging.warning(f'{filename} has no METADATA')
            continue 
        if 'DateTime' in meta_dict:
            datetime = process_timestamp(meta_dict['DateTime'])
        else: 
            logging.warning(f'{filename} has no DATETIME Data')
            continue 
        if 'GPSLatitude' in meta_dict:
            city = process_gps(meta_dict)
        else:
            logging.warning(f'{filename} has no GPS Data')
            city = ''

        ext = filename.rsplit('.', 1)[1]
        new_filename = f'{datetime["date"]}.{datetime["time"]}{i}{city}.{ext}'
        sort_file(filename, new_filename)
        i += 1

if __name__ == '__main__':
    main()