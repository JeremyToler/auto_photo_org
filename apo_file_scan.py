'''
Auto Photo Org File Scanner - Jeremy Toler
Scan's the input folder at a user defined interval [default: 5min]
If files are found, run apo.py. For more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import yaml
import time
import apo

def get_files(unsorted_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(unsorted_path):
        for name in filenames:
            files.append(os.path.join(dirpath, name))
    files.sort()
    return files

def main():
    config = yaml.load('config.yaml')

    while True:
        files = get_files(config['in_path'])
        if files:
            apo.main(files)
        time.sleep(config['wait_time'])

if __name__ == '__main__':
    main()