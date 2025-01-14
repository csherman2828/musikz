import json


class NoTokenInConfigException(Exception):
    pass


def _get_token(config_dict):
    if 'token' in config_dict:
        return config_dict['token']
    else:
        raise NoTokenInConfigException()


def _get_prefix(config_dict):
    if 'prefix' in config_dict.keys():
        return config_dict['prefix']
    else:
        return '!'

def _get_guilds(config_dict):
    if 'guilds' in config_dict.keys() and type(config_dict['guilds']) == dict:
        return [value for value in config_dict['guilds'].values()]
    else: 
        return []

# initialize globally to be accessed from imports
prefix = ''
token = ''
guilds = []

with open('config.json') as config_file:
    config_dict = json.load(config_file)
    token = _get_token(config_dict)
    prefix = _get_prefix(config_dict)
    guilds = _get_guilds(config_dict)
    print('guilds', guilds)

print('config token:', token)
print('config prefix:', prefix)
