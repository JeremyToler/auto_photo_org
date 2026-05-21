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
import apo_setup

def get_files():
    files = []
    for dirpath, dirnames, filenames in os.walk('/data/unsorted'):
        for name in filenames:
            files.append(os.path.join(dirpath, name))
    files.sort()
    return files

def main():
    apo_setup.setup()
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    while True:
        files = get_files()
        if not files:
            time.sleep(config['wait_time'])
            continue
        apo.main(files, config)
        time.sleep(config['wait_time'])

if __name__ == '__main__':
    main()