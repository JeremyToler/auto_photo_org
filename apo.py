# TODO Test png
# TODO Test gif
# TODO Test bmp
# TODO Test very old photos
# TODO Add video support
# TODO Test mp4
# TODO Test avi
# TODO Test mkv
# TODO Test very old video
# TODO Make a nice heading for this code
# pip install pillow, geopy
# TODO How do I make a requirements file?
# TODO Make sure readme file has all instructions for working with the code
# TODO Better logs (aut remove old logs, file per run)
# TimedRotatingFileHandler? part of logging module.

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from geopy.geocoders import Nominatim

unsorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\unsorted'
sorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\photos'

def get_files(unsorted_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(unsorted_path):
        files.extend(filenames)
        break # Stops walk from adding filenames in subdirectories.
    return files

def get_metadata(file_path):
    meta_dict = {}
    image = Image.open(file_path)
    exif = image._getexif()
    if exif:
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded == 'DateTime':
                meta_dict[decoded] = value
            if decoded == 'GPSInfo':
                for gps_tag in value:
                    gps_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    meta_dict[gps_decoded] = value[gps_tag]
    return meta_dict  

def process_timestamp(timestamp):
    date_object = datetime.strptime(timestamp, f'%Y:%m:%d %H:%M:%S')
    return date_object.strftime(f'%Y-%m-%d.%H%M%S') + '.'

def process_gps(meta_dict):
    geolocator = Nominatim(user_agent='auto_photo_org')
    latitude = convert_gps(*meta_dict['GPSLatitude'], 
                           meta_dict['GPSLatitudeRef'])
    longitude = convert_gps(*meta_dict['GPSLongitude'],
                            meta_dict['GPSLongitudeRef'])
    location = geolocator.reverse(
        f'{latitude}, {longitude}',
        zoom = 10,
        language='en-us'
        )
    return location.address.split(', ', 1)[0] + '.'

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
    new_path = os.path.join(sorted_path, new[:4])
    if not os.path.exists(sorted_path):
        os.mkdir(sorted_path)
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    os.rename(
        os.path.join(unsorted_path, old),
        os.path.join(new_path, new)
    )

def main():
    logtime = datetime.now()
    log = open('log.txt', 'a')
    print(logtime, 'Starting Batch Rename', file=log)
    for filename in get_files(unsorted_path):
        print(logtime, 'Processing:', filename, file=log)
        meta_dict = get_metadata(os.path.join(unsorted_path, filename))
        if not meta_dict:
            print('No Metadata:', filename, file=log)
            continue # Skip files that dont have Metadata
        if 'DateTime' in meta_dict:
            time = process_timestamp(meta_dict['DateTime'])
        else:
            print(logtime, 'No DateTime:', filename, file=log)
            continue # Skip files that dont have date/time
        if 'GPSLatitude' in meta_dict:
            city = process_gps(meta_dict)
        else:
            print(logtime, 'No GPS:', filename, file=log)
            city = ''
        # keep the ext and differentiate photos taken within 1 second
        end = filename[-7:]
        new_filename = f'{time}{city}{end}'
        sort_file(filename, new_filename)
        print(logtime, 'Success: New filename =', new_filename, file=log)
        log.close()

if __name__ == '__main__':
    main()