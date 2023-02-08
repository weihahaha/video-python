
import yaml

with open(r'configs\\config.yaml', 'r') as f:
    y= yaml.load(f,Loader=yaml.CLoader)
    

VIDEOPATH = y['videoPath']

REDISHOST = y['redis']['host']
REDISPORT = y['redis']['port']
REDISDB = y['redis']['db']

MONGOHOST = y['mongo']['host']
MONGOPORT = y['mongo']['port']
 
EMAIL_ADDRESS = y['emailAddress'] #发送邮箱地址
EMAIL_PASSWORD = y['emailPassword'] #发送的QQ邮箱SMTP的授权码


