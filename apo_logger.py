'''
Auto Photo Org Logger - Jeremy Toler
Makes 2 log files, one with all logs and one without debug logs.
For more info check the readme:
https://github.com/JeremyToler/auto_photo_org
'''
import logging
from datetime import datetime
import os

def setup_logger(name, log_file, level):
    format = logging.Formatter(
        '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
        )
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(format)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

format = '%Y-%m-%d_%H-%M'
timestamp = datetime.now().strftime(format)
debug = setup_logger('APO_ALL', f'logs/debug/{timestamp}.log', logging.DEBUG)
info = setup_logger('APO', f'logs/info/{timestamp}.log', logging.INFO)

def get_files():
    files = []
    for dirpath, dirnames, filenames in os.walk('logs/info'):
        for name in filenames:
            files.append(os.path.join(dirpath, name))
            files.sort(reverse=True)
    return files

def cleanup_logs(max_logs):
    files = get_files()
    while files > max_logs:
        oldest = files.pop()
        os.remove(f'logs/debug/{oldest}')
        os.remove(f'logs/info/{oldest}')
