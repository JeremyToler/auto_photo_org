import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

print(config['in_path'])
print(config['wait_time'])
print(config['slack']['use_slack'])