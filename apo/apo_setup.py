import random
import string
import yaml
from os import environ

def main():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    uid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    config['user_agent'] = f'APO-{uid}'
    config['alert_threshold'] = environ.get('ALERT_THRESHOLD', 10)
    config['max_logs'] = environ.get('MAX_LOGS', 100)
    config['wait_time'] = environ.get('WAIT_TIME', 86400)
    config['email']['use_email'] = environ.get('USE_EMAIL', False)
    config['email']['address'] = environ.get('EMAIL_ADDRESS')
    config['slack']['use_slack'] = environ.get('USE_SLACK', False)
    config['slack']['oauth'] = environ.get('SLACK_OAUTH')
    config['slack']['channel'] = environ.get('SLACK_CHANNEL')

    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

if __name__ == '__main__':
    main()