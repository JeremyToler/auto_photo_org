'''
Auto Photo Org Logger - Jeremy Toler
Makes 2 log files, one with all logs and one without debug logs.
For more info check the readme:
https://github.com/JeremyToler/auto_photo_org
'''
import logging
from datetime import datetime

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

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
debug = setup_logger('APO_ALL', f'logs/debug/{timestamp}.log', logging.DEBUG)
info = setup_logger('APO', f'logs/info/{timestamp}.log', logging.INFO)