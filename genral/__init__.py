from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')


TARGET_FILE = config.get('SETTING', 'TARGET_FILE')
