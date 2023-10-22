'''
Auto Photo Org - Jeremy Toler
Renames and sorts photos, for more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import re
import yaml
from exiftool import ExifToolHelper
from datetime import datetime
from geopy.geocoders import Nominatim
import apo_logger as log

config = yaml.load('config.yaml')

def get_metadata(files):
    meta_dict = {}
    with ExifToolHelper() as et:
        meta_dict = et.get_metadata(files)
    log.debug.debug(f'Meta_Dict: \n {meta_dict}')
    return meta_dict  

def get_gps(file):
    if 'Composite:GPSLatitude' in file.keys():
        # Sometimes metadata has the GPS tag but the value is ''
        if file['Composite:GPSLatitude']:
            log.debug.debug('GPS Metadata using key Composite:GPSLatitude')
            return(process_gps(file['Composite:GPSLatitude'], 
                        file['Composite:GPSLongitude']))
    elif 'EXIF:GPSLatitude' in file.keys():
        if file['EXIF:GPSLatitude']:
            log.debug.debug('GPS Metadata using key EXIF:GPSLatitude')
            lat = convert_gps(file['EXIF:GPSLatitude'], 
                            file['EXIF:GPSLatitudeRef'])
            lon = convert_gps(file['EXIF:GPSLongitude'], 
                            file['EXIF:GPSLongitudeRef'])
            return(process_gps(lat, lon))
    log.debug.warning('NO GPS DATA')
    return ''

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
def process_gps(lat, lon):
    log.debug.debug(f'GPS Lat: {lat} Lon: {lon}')
    geolocator = Nominatim(user_agent=uid)
    location = geolocator.reverse(
        f'{lat}, {lon}',
        zoom = 10,
        language='en-us'
        )
    city = location.address.split(', ', 1)[0].replace(' ', '_')
    log.debug.debug(f'GPS returned {location}')
    log.debug.debug(f'Extracted {city} from GPS Location.')
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
    log.debug.debug(f'Getting datetime from Metadata {key}: {metadata[key]}')
    try:
        dt = datetime.strptime(str(metadata[key])[:19], f'%Y:%m:%d %H:%M:%S')
        timestamp = dt.strftime(f'%Y-%m-%d.%H%M%S')
        log.debug.debug(f'Got full timestamp: {timestamp}')
    except:
        try:
            dt = datetime.strptime(str(metadata[key])[:10], f'%Y:%m:%d')
            timestamp = dt.strftime(f'%Y-%m-%d')
            log.debug.debug(f'Got partial timestamp: {timestamp}')
        except:
            log.debug.info(f'Failed to get timestamp from {key}')
            log.info.info(f'Failed to get timestamp from {key}')
            timestamp = ''
    return (timestamp)

'''
Most of the filenames that were made by a camera or phone have the date
in order YYYY MM DD along with other info. Removing all non digit
characters from the strings will put them all in the same order and
slicing the first 8 get rid of any none date numbers.
'''
def time_from_name(filename):
    log.debug.debug(f'Getting time from Filename: {filename}')
    stripped = re.sub(r'\D', '', filename.rsplit('.', 1)[0])[:8]
    if not stripped.startswith('20'):
        log.debug.warning(f'Could not extract time from {filename}')
        log.info.warning(f'Could not extract time from {filename}')
        log.debug.debug(f'{stripped} does not start with 20')
    try:
        dt = datetime.strptime(stripped[8], '%Y%m%d')
        return (dt.strftime(f'%Y-%m-%d'))
    except:
        log.debug.warning(f'Could not extract time from {filename}')
        log.info.warning(f'Could not extract time from {filename}')
        log.debug.debug(f'{stripped} is not in YYYMMDD format')
    return ('')

def sort_file(old_file, new_name):
    i = 0
    new_path = os.path.join(config.out_path, new_name[:4])
    new_file = os.path.join(new_path, new_name)
    if not os.path.exists(config.out_path):
        os.mkdir(config.out_path)
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
            log.debug.info(f'{old_file} has been renamed {new_file}')
            log.info.info(f'{old_file} has been renamed {new_file}')
            break

def main(files):
    meta_dict = get_metadata(files)
    for file in meta_dict:
        log.debug.info(f'Starting {file["SourceFile"]}')
        log.info.info(f'Starting {file["SourceFile"]}')
        timestamp = get_time(file)
        if not timestamp: 
            log.debug.error(f'Unable to get date. Skipping File')
            log.info.error(f'Unable to get date. Skipping File')
            continue
        try:
            city = get_gps(file)
        except:
            log.debug.exception(f'GPS Error. Skipping File to try again later')
            log.info.exception(f'GPS Error. Skipping File to try again later')
            continue
        ext = file['File:FileName'].rsplit('.', 1)[1]
        new_name = f'{timestamp}{city}.{ext}'
        sort_file(file['SourceFile'], new_name)

if __name__ == '__main__':
    main()