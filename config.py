import os
import configparser

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')

def get_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config['DATABASE'] = {'initialized': 'false'}
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    return config

def is_database_initialized():
    config = get_config()
    initialized = config['DATABASE'].getboolean('initialized')
    return initialized

def set_database_initialized():
    config = get_config()
    config['DATABASE']['initialized'] = 'true'
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

