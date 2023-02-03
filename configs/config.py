
import yaml

with open(r'configs\\config.yaml', 'r') as f:
    y= yaml.load(f,Loader=yaml.CLoader)
    print(y)

VIDEOPATH = y['videoPath']

REDISHOST = y['redis']['host']
REDISPORT = y['redis']['port']
REDISDB = y['redis']['db']

MONGOHOST = y['mongo']['host']
MONGOPORT = y['mongo']['port']


