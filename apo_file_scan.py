'''
Auto Photo Org File Scanner - Jeremy Toler
Scan's the input folder at a user defined interval [default: 1hr]
If files are found, run apo.py. For more info check the readme
https://github.com/JeremyToler/auto_photo_org
'''
import os
import yaml
import time
import apo

def get_files(in_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(in_path):
        for name in filenames:
            files.append(os.path.join(dirpath, name))
    files.sort()
    return files

def main():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    while True:
        print('Looping')
        files = get_files(config['in_path'])
        if files:
            print('Files Found')
            apo.main(files, config)
        time.sleep(config['wait_time'])

if __name__ == '__main__':
    main()