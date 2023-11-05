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

def new_log():
    format = '%Y-%m-%d_%H-%M'
    timestamp = datetime.now().strftime(format)
    if not os.path.exists('/data/logs'):
        os.mkdir('/data/logs')
    log = setup_logger('APO', f'/data/logs/{timestamp}.log', logging.DEBUG)
    return(log)

def get_files():
    files = []
    for dirpath, dirnames, filenames in os.walk('/data/logs/'):
        for name in filenames:
            files.append(os.path.join(name))
            files.sort(reverse=True)
    return files

def cleanup_logs(max_logs, log):
    files = get_files()
    while len(files) > max_logs:
        oldest = files.pop()
        log.debug(f'Removing "/data/logs/{oldest}"')
        os.remove(f'/data/logs/{oldest}')

