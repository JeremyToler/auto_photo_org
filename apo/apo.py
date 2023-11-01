'''
Auto Photo Org - Jeremy Toler
Renames and sorts photos, for more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import re
from exiftool import ExifToolHelper
from datetime import datetime
from geopy.geocoders import Nominatim
import apo_logger
import apo_slack
import apo_email

def get_metadata(files, log):
    meta_dict = {}
    with ExifToolHelper() as et:
        meta_dict = et.get_metadata(files)
    log.debug(f'Meta_Dict: \n {meta_dict}')
    return meta_dict  

def get_gps(file, user_agent, log):
    if 'Composite:GPSLatitude' in file.keys():
        # Sometimes metadata has the GPS tag but the value is ''
        if file['Composite:GPSLatitude']:
            log.debug('GPS Metadata using key Composite:GPSLatitude')
            return(process_gps(
                file['Composite:GPSLatitude'],
                file['Composite:GPSLongitude'],
                user_agent, log
                ))
    elif 'EXIF:GPSLatitude' in file.keys():
        if file['EXIF:GPSLatitude']:
            log.debug('GPS Metadata using key EXIF:GPSLatitude')
            lat = convert_gps(
                file['EXIF:GPSLatitude'],
                file['EXIF:GPSLatitudeRef']
                )
            lon = convert_gps(
                file['EXIF:GPSLongitude'],
                file['EXIF:GPSLongitudeRef']
                )
            return(process_gps(lat, lon, user_agent), log)
    log.info('NO GPS DATA')
    return ''

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
def process_gps(lat, lon, user_agent, log):
    log.debug(f'GPS Lat: {lat} Lon: {lon}')
    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.reverse(
        f'{lat}, {lon}',
        zoom = 10,
        language='en-us'
        )
    city = location.address.split(', ', 1)[0].replace(' ', '_')
    log.debug(f'GPS returned {location}')
    log.debug(f'Extracted {city} from GPS Location.')
    return '.' + re.sub(r'[^(A-Z)(a-z)(0-9)_]', '', city)

def convert_gps(pos, ref):
    if ref in ['W', 'S']:
        return pos * -1
    else:
        return pos

def get_time(metadata, log):
    meta_priority = [
        'EXIF:DateTimeOriginal', 
        'EXIF:CreateDate',
        'Composite:GPSDateTime',
        'Composite:SubSecCreateDate',
        'Composite:SubSecDateTimeOriginal',
        'QuickTime:MediaCreateDate',
        'QuickTime:TrackCreateDate',
        'EXIF:GPSDateStamp',
        'File:FileModifyDate',
        'File:FileInodeChangeDate'
                     ]
    timestamp = ''
    for key in meta_priority:
        if key in metadata.keys():
            timestamp = time_from_metadata(key, metadata, log)
        if timestamp: break
    else:
        timestamp = time_from_name(metadata['File:FileName'], log)
    return timestamp

def time_from_metadata(key, metadata, log):
    log.debug(f'Getting datetime from Metadata {key}: {metadata[key]}')
    try:
        dt = datetime.strptime(str(metadata[key])[:19], f'%Y:%m:%d %H:%M:%S')
        timestamp = dt.strftime(f'%Y-%m-%d.%H%M%S')
        log.debug(f'Got full timestamp: {timestamp}')
    except:
        try:
            dt = datetime.strptime(str(metadata[key])[:10], f'%Y:%m:%d')
            timestamp = dt.strftime(f'%Y-%m-%d')
            log.debug(f'Got partial timestamp: {timestamp}')
        except:
            log.info(f'Failed to get timestamp from {key}')
            timestamp = ''
    return (timestamp)

'''
Most of the filenames that were made by a camera or phone have the date
in order YYYY MM DD along with other info. Removing all non digit
characters from the strings will put them all in the same order and
slicing the first 8 get rid of any none date numbers.
'''
def time_from_name(filename, log):
    log.debug(f'Getting time from Filename: {filename}')
    stripped = re.sub(r'\D', '', filename.rsplit('.', 1)[0])[:8]
    if not stripped.startswith('20'):
        log.warning(f'Could not extract time from {filename}')
        log.debug(f'{stripped} does not start with 20')
    try:
        dt = datetime.strptime(stripped[8], '%Y%m%d')
        return (dt.strftime(f'%Y-%m-%d'))
    except:
        log.warning(f'Could not extract time from {filename}')
        log.debug(f'{stripped} is not in YYYMMDD format')
    return ('')

def sort_file(old_file, new_name, log):
    i = 0
    new_path = os.path.join('/sorted/', new_name[:4])
    new_file = os.path.join(new_path, new_name)
    if not os.path.exists('/sorted/'):
        os.mkdir('/sorted/')
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
            log.info(f'{old_file} has been renamed {new_file}')
            break

def alerts(file_count, config, log):
    if config['slack']['use_slack'] == 'true':
        apo_slack.send_alert(
            file_count,
            config['slack']['oauth'],
            config['slack']['channel'],
            log
            )
    if config['email']['use_email'] == 'true':
        apo_email.send_alert(
            file_count,
            config['email']['address'],
            log
        )

def main(files, config, alert):
    log = apo_logger.new_log()
    log.debug(f'Found Files: \n {files}')
    meta_dict = get_metadata(files, log)
    for file in meta_dict:
        log.info(f'Starting {file["SourceFile"]}')
        timestamp = get_time(file, log)
        if not timestamp: 
            log.error(f'Unable to get date. Skipping File')
            continue
        try:
            city = get_gps(file, config['user_agent'], log)
        except:
            log.exception(f'GPS Error. Skipping File to try again later')
            continue
        ext = file['File:FileName'].rsplit('.', 1)[1]
        new_name = f'{timestamp}{city}.{ext}'
        sort_file(file['SourceFile'], new_name, log)
    if alert:
        alerts(len(files), config, log)
    apo_logger.cleanup_logs(config['max_logs'], log)

if __name__ == '__main__':
    main()