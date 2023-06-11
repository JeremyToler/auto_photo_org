# TODO Make a nice heading for this code
# TODO Does needed directory exist?
### if os.path.exists('file_path')
# TODO Make the needed directory
### os.mkdir(path to directory)
### https://www.geeksforgeeks.org/create-a-directory-in-python/#
# TODO rename and move the file
### https://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
# TODO Test jpg
# TODO Test png
# TODO Test gif
# TODO Test bmp
# TODO Test very old photos
# TODO Add video support
# TODO Test mp4
# TODO Test avi
# TODO Test mkv
# TODO Test very old video
# TODO How do I make a requirements file?
# TODO Make sure readme file has all instructions for working with the code

from os import walk
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

unsorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\unsorted'
sorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\photos'

def get_files(unsorted_path):
    files = []
    for (dirpath, dirnames, filenames) in walk(unsorted_path):
        files.extend(filenames)
        break # Stops walk from adding filenames in subdirectories.
    return files

def sort_file(filename):
    pass

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
    return date_object.strftime(f'%Y-%m-%d.%H%M%S')

def process_gps(latitude, longitude):
    return "CITY"

def main():
    for filename in get_files(unsorted_path):
        filepath = f'{unsorted_path}\\{filename}'
        meta_dict = get_metadata(filepath)
        time = process_timestamp(meta_dict['DateTime'])
        city = process_gps(meta_dict['GPSLatitude'], meta_dict['GPSLongitude'])
        # keep the ext and differentiate photos taken within 1 second
        end = filename[-7:]
        new_filename = f'{time}.{city}.{end}'
        print(new_filename)

if __name__ == '__main__':
    main()