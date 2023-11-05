import random
import string
import yaml
from os import environ

def get_bool(env_name):
    env_value = str(environ.get(f'{env_name}', 'false'))
    t = ('true', '1', 't', 'y', 'yes', 'on')
    f = ('false', '0', 'f', 'n', 'no', 'off')
    if env_value.lower() in f:
        return 'false'
    elif env_value.lower() in t:
        return 'true'
    else:
        raise ValueError(f'{env_value} is not a valid value for {env_name}')

def setup():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    uid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    config['user_agent'] = f'APO-{uid}'
    config['alert_threshold'] = int(environ.get('ALERT_THRESHOLD', 10))
    config['max_logs'] = int(environ.get('MAX_LOGS', 100))
    config['wait_time'] = int(environ.get('WAIT_TIME', 86400))
    config['slack']['use_slack'] = get_bool('USE_SLACK')
    config['slack']['oauth'] = environ.get('SLACK_OAUTH')
    config['slack']['channel'] = environ.get('SLACK_CHANNEL')

    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)