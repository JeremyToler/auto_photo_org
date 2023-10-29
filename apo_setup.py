import random
import string
import yaml

def main():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    uid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    config['user_agent'] = f'APO-{uid}'

    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

if __name__ == '__main__':
    main()