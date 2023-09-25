'''
Auto Photo Org - Jeremy Toler
Renames and sorts photos, for more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''

#TODO Make installer
#TODO Script to install exiftool, https://pypi.org/project/PyExifTool/
#TODO Automate Noninatum Key generation

import os
import config
import logging
import re
from exiftool import ExifToolHelper
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
    for dirpath, dirnames, filenames in os.walk(unsorted_path):
        for name in filenames:
            files.append(os.path.join(dirpath, name))
    if not files:
        logging.info(f'{unsorted_path} is empty')
    files.sort()
    logging.debug(f'Found Files: \n {files}')
    return files

def get_metadata(files):
    meta_dict = {}
    with ExifToolHelper() as et:
        meta_dict = et.get_metadata(files)
    logging.debug(f'Meta_Dict: \n {meta_dict}')
    return meta_dict  

def get_gps(file):
    if 'Composite:GPSLatitude' in file.keys():
        return(process_gps(file['Composite:GPSLatitude'], 
                    file['Composite:GPSLongitude']))
    elif 'EXIF:GPSLatitude' in file.keys():
        lat = convert_gps(file['EXIF:GPSLatitude'], 
                          file['EXIF:GPSLatitudeRef'])
        lon = convert_gps(file['EXIF:GPSLongitude'], 
                          file['EXIF:GPSLongitudeRef'])
        return(process_gps(lat, lon))
    else:
        logging.warning('NO GPS DATA')
        return ''

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
def process_gps(lat, lon):
    geolocator = Nominatim(user_agent=config.user_agent)
    location = geolocator.reverse(
        f'{lat}, {lon}',
        zoom = 10,
        language='en-us'
        )
    city = location.address.split(', ', 1)[0].replace(' ', '_')
    logging.debug(f'GPS returned {location}')
    logging.debug(f'Extracted {city} from GPS Location.')
    return '.' + re.sub(r'[^(A-Z)(a-z)(0-9)_]', '', city)
    
def convert_gps(pos, ref):
    if ref in ['W', 'S']:
        return pos * -1
    else:
        return pos

def get_time(metadata):
    meta_priority = ['EXIF:DateTimeOriginal', 
                     'EXIF:CreateDate',
                     'Composite:GPSDateTime',
                     'Composite:SubSecCreateDate',
                     'Composite:SubSecDateTimeOriginal',
                     'QuickTime:MediaCreateDate',
                     'QuickTime:TrackCreateDate',
                     'EXIF:GPSDateStamp',
                     'File:FileModifyDate',
                     'File:FileInodeChangeDate']
    timestamp = ''
    for key in meta_priority:
        if key in metadata.keys():
            timestamp = time_from_metadata(key, metadata)
            if timestamp:
                break
    else:
        timestamp = time_from_name(metadata['File:FileName'])
    return timestamp

def time_from_metadata(key, metadata):
    logging.debug(f'Getting datetime from Metadata {key}: {metadata[key]}')
    try:
        dt = datetime.strptime(str(metadata[key])[:19], f'%Y:%m:%d %H:%M:%S')
        timestamp = dt.strftime(f'%Y-%m-%d.%H%M%S')
        logging.debug(f'Got full timestamp: {timestamp}')
    except:
        try:
            dt = datetime.strptime(str(metadata[key])[:10], f'%Y:%m:%d')
            timestamp = dt.strftime(f'%Y-%m-%d')
            logging.debug(f'Got partial timestamp: {timestamp}')
        except:
            logging.info(f'Failed to get timestamp from {key}')
            timestamp = ''
    return (timestamp)

'''
Most of the filenames that were made by a camera or phone have the date
in order YYYY MM DD along with other info. Removing all non digit
characters from the strings will put them all in the same order and
slicing the first 8 get rid of any none date numbers.
'''
def time_from_name(filename):
    logging.debug(f'Getting time from Filename: {filename}')
    stripped = re.sub(r'\D', '', filename.rsplit('.', 1)[0])[:8]
    if not stripped.startswith('20'):
        logging.warning(f'Could not extract time from {filename}')
        logging.debug(f'{stripped} does not start with 20')
    try:
        dt = datetime.strptime(stripped[8], '%Y%m%d')
        return (dt.strftime(f'%Y-%m-%d'))
    except:
        logging.warning(f'Could not extract time from {filename}')
        logging.debug(f'{stripped} is not in YYYMMDD format')
    return ('')

def sort_file(old_file, new_name):
    i = 0
    new_path = os.path.join(config.sorted_path, new_name[:4])
    new_file = os.path.join(new_path, new_name)
    if not os.path.exists(config.sorted_path):
        os.mkdir(config.sorted_path)
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    while True:
        split_name = new_file.rsplit('.', 1)
        if i > 0:
            tmp_name = split_name[0].rsplit('.', 1)
            new_file = f'{tmp_name[0]}.{i:04d}.{split_name[1]}'
        else:
            new_file = f'{split_name[0]}.{i:04d}.{split_name[1]}'
        i += 1
        if not os.path.isfile(new_file):
            os.rename(old_file, new_file)
            logging.info(f'{old_file} has been renamed {new_file}')
            break

def main():
    files = get_files(config.unsorted_path)
    meta_dict = get_metadata(files)
    for file in meta_dict:
        logging.info(f'Starting {file["SourceFile"]}')
        timestamp = get_time(file)
        if not timestamp: 
            logging.error(f'Unable to get date. Skipping File')
            continue
        try:
            city = get_gps(file)
        except:
            logging.exception(f'GPS Error. Skipping File to try again later')
            continue
        ext = file['File:FileName'].rsplit('.', 1)[1]
        new_name = f'{timestamp}{city}.{ext}'
        sort_file(file['SourceFile'], new_name)

if __name__ == '__main__':
    main()