import random
import string
import yaml
from os import environ

def setup():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    uid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    config['user_agent'] = f'APO-{uid}'
    config['max_logs'] = int(environ.get('MAX_LOGS', 100))
    config['wait_time'] = int(environ.get('WAIT_TIME', 86400))

    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)