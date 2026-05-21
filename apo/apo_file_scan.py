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

def get_files(unsorted_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(unsorted_path):
        for name in filenames:
            if not name.startswith('.'):
                files.append(os.path.join(dirpath, name))
    files.sort()
    return files

def main():
    apo_setup.setup()
    with open(apo_setup.CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    while True:
        files = get_files(config['unsorted_path'])
        if not files:
            time.sleep(config['wait_time_minutes'] * 60)
            continue
        apo.main(files, config)
        time.sleep(config['wait_time_minutes'] * 60)

if __name__ == '__main__':
    main()