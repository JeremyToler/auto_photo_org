import os
import random
import string
import yaml
from os import environ

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')

def setup():
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    uid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    config['user_agent'] = f'APO-{uid}'
    config['max_logs'] = int(environ.get('MAX_LOGS', 100))
    config['wait_time_minutes'] = int(environ.get('WAIT_TIME_MINUTES', 1440))
    config['renumber_all'] = environ.get('RENUMBER_ALL', 'false').lower() in ('true', '1', 'y', 'yes', 'on')
    config['gps_retry_limit'] = int(environ.get('GPS_RETRY_LIMIT', 3))
    config['unsorted_path'] = environ.get('UNSORTED_PATH', '/data/unsorted')
    config['sorted_path'] = environ.get('SORTED_PATH', '/data/sorted')
    config['logs_path'] = environ.get('LOGS_PATH', '/data/logs')

    with open(CONFIG_PATH, 'w') as file:
        yaml.dump(config, file)