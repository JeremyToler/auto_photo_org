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
    last_file_count = 0
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    while True:
        alert = False
        files = get_files(config['in_path'])
        if not files:
            last_file_count = 0
            continue
        file_count = len(files)
        if all (
            file_count == last_file_count, 
            file_count >= config['alert_threshold']
            ):
            alert = True
        apo.main(files, config, alert)
        last_file_count = file_count
        time.sleep(config['wait_time'])

if __name__ == '__main__':
    main()