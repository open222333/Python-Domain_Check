from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')


GET_IMAGE_CHECK_URL = config.get(
    'IMAGE', 'GET_IMAGE_CHECK_URL',
    fallback='https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
)
