'''
Auto Photo Org - Jeremy Toler
Renames and sorts photos, for more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import shutil
import re
from exiftool import ExifToolHelper
from datetime import datetime
from geopy.geocoders import Nominatim
import apo_logger

def get_metadata(files, log):
    meta_dict = {}
    with ExifToolHelper() as et:
        meta_dict = et.get_metadata(files)
    log.debug(f'Meta_Dict: \n {meta_dict}')
    return meta_dict  

def get_gps(file, user_agent, log):
    if 'Composite:GPSLatitude' in file.keys() and file['Composite:GPSLatitude']:
        log.debug('GPS Metadata using key Composite:GPSLatitude')
        return process_gps(file['Composite:GPSLatitude'], file['Composite:GPSLongitude'], user_agent, log)
    if 'EXIF:GPSLatitude' in file.keys() and file['EXIF:GPSLatitude']:
        log.debug('GPS Metadata using key EXIF:GPSLatitude')
        lat = convert_gps(file['EXIF:GPSLatitude'], file['EXIF:GPSLatitudeRef'])
        lon = convert_gps(file['EXIF:GPSLongitude'], file['EXIF:GPSLongitudeRef'])
        return process_gps(lat, lon, user_agent, log)
    log.info('NO GPS DATA')
    return ''

def process_gps(lat, lon, user_agent, log):
    """Use geopy to interact with the Nominatim (OpenStreetMap) API.
    At zoom level 10 Address returns City, County, State, Country.
    """
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
            timestamp = verify_time(time_from_metadata(key, metadata, log))
        if timestamp: break
    else:
        timestamp = verify_time(time_from_name(metadata['File:FileName'], log))
    return timestamp

def verify_time(timestamp):
    if datetime.strptime(timestamp[:10], f'%Y-%m-%d') > datetime.now():
        return('')
    else:
        return(timestamp)

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

def time_from_name(filename, log):
    """Most filenames from a camera or phone have the date in YYYY MM DD order.
    Stripping non-digits and slicing to 8 characters normalises them all.
    """
    log.debug(f'Getting time from Filename: {filename}')
    stripped = re.sub(r'\D', '', filename.rsplit('.', 1)[0])[:8]
    if not stripped.startswith('20'):
        log.warning(f'Could not extract time from {filename}')
        log.debug(f'{stripped} does not start with 20')
        return ''
    try:
        dt = datetime.strptime(stripped[:8], '%Y%m%d')
        return dt.strftime('%Y-%m-%d')
    except:
        log.warning(f'Could not extract time from {filename}')
        log.debug(f'{stripped} is not in YYYMMDD format')
    return ''

def sort_file(old_file, new_name, log):
    i = 0
    year_folder = os.path.join('/data/sorted/', new_name[:4])
    new_file = os.path.join(year_folder, new_name)
    if not os.path.exists('/data/sorted/'):
        os.mkdir('/data/sorted/')
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)
    while True:
        split_name = new_file.rsplit('.', 1)
        if i > 0:
            tmp_name = split_name[0].rsplit('.', 1)
            new_file = f'{tmp_name[0]}.{i:04d}.{split_name[1]}'
        else:
            new_file = f'{split_name[0]}.{i:04d}.{split_name[1]}'
        i += 1
        if not os.path.isfile(new_file):
            shutil.copy(old_file, new_file)
            os.remove(old_file)
            log.info(f'{old_file} has been renamed {new_file}')
            break
    return year_folder

def apply_numbering(folders, log):
    """Post-process sorted folders to apply clean numbering.
    Single files have their counter stripped. Duplicates are renumbered
    from 1 with only as many leading zeros as the group size requires.
    A temp-rename pass is used to avoid conflicts during renaming.
    """
    for folder in folders:
        if not os.path.exists(folder):
            continue
        groups = {}
        for fname in sorted(os.listdir(folder)):
            if not os.path.isfile(os.path.join(folder, fname)):
                continue
            match = re.match(r'^(.+)\.\d{4}\.([^.]+)$', fname)
            if not match:
                continue
            base, ext = match.group(1), match.group(2)
            groups.setdefault(base, []).append((fname, ext))

        for base, files in groups.items():
            if len(files) == 1:
                fname, ext = files[0]
                old_path = os.path.join(folder, fname)
                new_path = os.path.join(folder, f'{base}.{ext}')
                if os.path.exists(new_path):
                    log.warning(f'Skipping rename, file already exists: {new_path}')
                    continue
                os.rename(old_path, new_path)
                log.info(f'{old_path} renamed to {new_path}')
            else:
                width = len(str(len(files)))
                temp_paths = []
                for fname, _ in files:
                    old_path = os.path.join(folder, fname)
                    temp_path = old_path + '.tmp'
                    os.rename(old_path, temp_path)
                    temp_paths.append(temp_path)
                for i, (temp_path, (_, ext)) in enumerate(zip(temp_paths, files), start=1):
                    new_path = os.path.join(folder, f'{base}.{i:0{width}}.{ext}')
                    os.rename(temp_path, new_path)
                    log.info(f'Renamed to {new_path}')


def main(files, config):
    log = apo_logger.new_log()
    log.debug(f'Config: \n {config}')
    log.debug(f'Found Files: \n {files}')
    meta_dict = get_metadata(files, log)
    touched_folders = set()
    for file in meta_dict:
        log.info(f'Starting {file["SourceFile"]}')
        timestamp = get_time(file, log)
        if not timestamp: 
            log.error('Unable to get date. Skipping File')
            continue
        try:
            city = get_gps(file, config['user_agent'], log)
        except:
            log.exception('GPS Error. Skipping File to try again later')
            continue
        try:
            ext = file['File:FileName'].rsplit('.', 1)[1]
        except:
            log.exception(f'File {file["File:FileName"]} has no extension')
            continue
        new_name = f'{timestamp}{city}.{ext}'
        year_folder = sort_file(file['SourceFile'], new_name, log)
        if year_folder:
            touched_folders.add(year_folder)

    if config['renumber_all']:
        sorted_root = '/data/sorted/'
        folders = [
            os.path.join(sorted_root, d) for d in os.listdir(sorted_root)
            if os.path.isdir(os.path.join(sorted_root, d))
        ] if os.path.exists(sorted_root) else []
    else:
        folders = touched_folders

    if folders:
        apply_numbering(folders, log)

    apo_logger.cleanup_logs(config['max_logs'], log)

if __name__ == '__main__':
    main()