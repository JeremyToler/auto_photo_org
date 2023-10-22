'''
Auto Photo Org File Scanner - Jeremy Toler
Scan's the input folder at a user defined interval [default: 5min]
If files are found, run apo.py. For more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import apo

def main():
    files = get_files(unsorted_path)
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