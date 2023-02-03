import pymongo

from configs.config import *


conn_str = f"mongodb://{MONGOHOST}:{MONGOPORT}/"
client: pymongo.MongoClient = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

try:
    version = client.server_info()['version']
    print(f'mongo---{version}---OK')
except Exception:
    print("Mongo无法连接到服务器。")

usersDb = client['user-database']['info']
usersDb.create_index('pid')
userVideoPperation = client['user-database']['userVideoPperation']
userVideoPperation.create_index('pid')

videoInfoDb = client['video-database']['info']
videoInfoDb.create_index('pid')
videoVarietyNumDb = client['video-database']['varietyNum']
videoVarietyNumDb.create_index('pid')
videoCommentsDb = client['video-database']['comments']
videoCommentsDb.create_index('pid')

import redis
 
redis_pool = redis.ConnectionPool(host=REDISHOST, port= REDISPORT,  db= REDISDB, decode_responses=True)
redis_conn: redis.client.Redis = redis.Redis(connection_pool= redis_pool)
try:
    redis_version = redis_conn.info()['redis_version']
    print(f'redis---{redis_version}---OK')
except Exception:
    print("Redis无法连接到服务器。")

