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
    return date_object.strftime(f'%Y-%m-%d.%H%M%S') + '.'

'''
Use geopy to interact with the Nominatim (OpenStreetMap) API
At zoom level 10 Address returns City, County, State, Country
'''
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
    # TODO Better logging, with logging module
    logtime = datetime.now()
    log = open('log.txt', 'a')
    print(logtime, 'Starting Batch Rename', file=log)

    for filename in get_files(unsorted_path):
        print(logtime, 'Processing:', filename, file=log)
        meta_dict = get_metadata(os.path.join(unsorted_path, filename))

        # TODO Move this error checking to its own function.
        if not meta_dict: 
            print(logtime, 'No Metadata:', filename, file=log)
            continue 
        if 'DateTime' in meta_dict:
            time = process_timestamp(meta_dict['DateTime'])
        else: 
            print(logtime, 'No DateTime:', filename, file=log)
            continue 
        if 'GPSLatitude' in meta_dict:
            city = process_gps(meta_dict)
        else:
            print(logtime, 'No GPS:', filename, file=log)
            city = ''

        # TODO Make a better per file stamp. More reliably get the ext. 
        end = filename[-7:]
        new_filename = f'{time}{city}{end}'
        sort_file(filename, new_filename)
        print(logtime, 'Success: New filename =', new_filename, file=log)
    log.close()

if __name__ == '__main__':
    main()