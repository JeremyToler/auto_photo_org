'''
Auto Photo Org - Jeremy Toler
Renames and sorts photos, for more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import config
import logging
import re
import slack_sdk as slack
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
    if not files:
        logging.info(f'{unsorted_path} is empty')
    return sorted(files)

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
        if decoded == 'GPSInfo':
            gps_tag = tag
            logging.debug('GPS Metadata Detected')
        elif not str(value).find('0000:00:00') == -1:
            logging.debug('Empty Timestamp found')
        else:
            meta_dict[decoded] = value
    if gps_tag:
        for tag, value in exif[gps_tag].items():
            decoded = GPSTAGS.get(tag, tag)
            meta_dict[decoded] = value
    return meta_dict  

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
def process_gps(meta_dict):
    geolocator = Nominatim(user_agent=config.user_agent)
    latitude = convert_gps(*meta_dict['GPSLatitude'], 
                           meta_dict['GPSLatitudeRef'])
    longitude = convert_gps(*meta_dict['GPSLongitude'],
                            meta_dict['GPSLongitudeRef'])
    location = geolocator.reverse(
        f'{latitude}, {longitude}',
        zoom = 10,
        language='en-us'
        )
    try:
        city = location.address.split(', ', 1)[0].replace(' ', '_')
    except:
        return ''
    else:
        return '.' + re.sub(r'[^(A-Z)(a-z)(0-9)_]', '', city)

'''
Pillow returns GPS coordinates as Degrees, Minutes, Seconds
Nominatim expects GPS coordinates to be Decimal Degrees
'''
def convert_gps(deg, min, sec, ref):
    result = float(deg) + float(min) / 60 + float(sec) / 3600
    if ref in ['W', 'S']:
        result = result * -1
    return result

def get_time(meta_dict, filename):
    date = ''
    time = ''
    if 'DateTimeOriginal' in meta_dict:
        date, time = time_from_metadata('DateTimeOriginal', meta_dict)
    if not date and 'DateTime' in meta_dict:
        date, time = time_from_metadata('DateTime', meta_dict)
    if not date:
        date, time = time_from_name(filename)
    if not date and 'GPSDateStamp' in meta_dict:
        date, time = time_from_metadata('GPSDateStamp', meta_dict)
    if not date:
        date, time = time_from_file_data(filename)
    return (date, time)

def time_from_metadata(key, meta_dict):
    logging.debug(f'Getting datetime from Metadata {key}: {meta_dict[key]}')
    try:
        timestamp = datetime.strptime(str(meta_dict[key]), f'%Y:%m:%d %H:%M:%S')
        date = timestamp.strftime(f'%Y-%m-%d')
        time = '.' + timestamp.strftime(f'%H%M%S')
        logging.debug('Got date and time')
    except:
        try:
            timestamp = datetime.strptime(meta_dict[key], f'%Y:%m:%d')
            date = timestamp.strftime(f'%Y-%m-%d')
            time = ''
            logging.debug('Got date, could not parse time')
        except:
            date = ''
            time = ''
            logging.debug(f'Failed to get date or time from {key}')
    return (date, time)

def time_from_file_data(filename):
    filepath = os.path.join(config.unsorted_path, filename)
    timestamp = datetime.fromtimestamp(os.path.getctime(filepath))
    logging.debug(f'Getting time from file creation date {timestamp}')
    date = timestamp.strftime(f'%Y-%m-%d')
    time = '.' + timestamp.strftime(f'%H%M%S')
    return (date, time)

'''
Most of the filenames that were made by a camera or phone have the date
in order YYYY MM DD HH MM SS along with other info such as PXL as well
as other formatting. Removing all non digit characters from the strings
will put them all in the same order and slicing the first 14 get rid of
numbering or milliseconds.
'''
def time_from_name(filename):
    logging.debug(f'Getting time from Filename')
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
        newname = re.sub(r'(\.\d\d\d\d)', '', split_name[0])
        new_file = f'{newname}.{i:04d}.{split_name[1]}'
        i += 1
    else:
        os.rename(old_file, new_file)
    logging.info(f'{old_file} has been renamed {new_file}')

def manual_sort_check():
    unsorted_count = len(get_files(config.unsorted_path))
    if unsorted_count > config.alert_threshold:
        if len(config.slack_oauth) < 50:
            logging.info('Slack not enabled or invalid oauth')
        else:
            client = slack.WebClient(token=config.slack_oauth)
            client.chat_postMessage(
                channel=config.slack_channel,
                text=f'{unsorted_count} files need to be manually sorted',
                icon_emoji = ':camera:',
                username = 'apo'
                )        

def main():
    for filename in get_files(config.unsorted_path):
        logging.debug(f'Processing {filename}')
        meta_dict = get_metadata(os.path.join(config.unsorted_path, filename))
        date, time = get_time(meta_dict, filename)
        if not date: 
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
                logging.exception(f'Unable to process GPS for {filename}')
                continue
        else:
            logging.warning(f'{filename} has no GPS Data')
            city = ''
        ext = filename.rsplit('.', 1)[1]
        new_filename = f'{date}{time}{city}.{ext}'
        sort_file(filename, new_filename)
    manual_sort_check()

if __name__ == '__main__':
    main()