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

def new_log(logs_path):
    format = '%Y-%m-%d_%H-%M'
    timestamp = datetime.now().strftime(format)
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)
    log = setup_logger(f'APO_{timestamp}', os.path.join(logs_path, f'{timestamp}.log'), logging.DEBUG)
    return log, timestamp

def get_timestamps(logs_path):
    """Return a sorted list of unique run timestamps found in the logs folder."""
    timestamps = set()
    for name in os.listdir(logs_path):
        timestamps.add(name.split('.')[0])
    return sorted(timestamps, reverse=True)

def cleanup_logs(max_logs, logs_path, log):
    """Delete oldest runs (all files sharing a timestamp) until under the limit."""
    timestamps = get_timestamps(logs_path)
    while len(timestamps) > max_logs:
        oldest = timestamps.pop()
        for name in os.listdir(logs_path):
            if name.startswith(oldest):
                log.debug(f'Removing {os.path.join(logs_path, name)}')
                os.remove(os.path.join(logs_path, name))

