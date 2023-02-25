import random
import string
import time
import uuid
from bson.objectid import ObjectId

from flask import Blueprint, abort, request, jsonify, make_response
from public.publics import isImage, isUser, md5_string, makeResponse

from verification.verifications import MapVer, Bakedin, StrVer
from models.models import redis_conn, usersDb, userVideoPperation, usersIcon, videoInfoDb

userApp = Blueprint('userApp', __name__, url_prefix='/users')

# 注册
@userApp.route('/register', methods=['POST'])
def register():
    
    data: dict = MapVer(request.get_json(), 
                        Bakedin(key='name', max=15, min=3, required=True), 
                        Bakedin(key='pwd', max=15, min=5, required=True), 
                        Bakedin(key='email', max=150, required=True),
                        Bakedin(key='code', max=8, required=True),
                        Bakedin(key='iconbase64', max=10*1024, required=True))
    
    emaCode = redis_conn.get(data['email'])
    if emaCode != data['code']:
        abort(makeResponse(-1, f'验证码错误'))

    dtas = usersDb.find_one({'$or': [{'name':data['name']}, {'email': data['email']}]})
    if  dtas is not None:
        if dtas['name'] == data['name']:
            abort(makeResponse(-2, '用户名称已存在'))
        if dtas['email'] == data['email']:
            abort(makeResponse(-3, '邮箱已被使用'))

    if isImage(data['iconbase64']) is False:
        abort(makeResponse(-3, '格式不正确'))

    userId = uuid.uuid5(uuid.uuid4(), uuid.uuid4().hex).hex[0: 24]
    person = {
        'pid': userId,
        'name': data['name'],
        'pwd': data['pwd'],
        'email': data['email'],
        'time': time.time(),
        'permissions': 'ordinary',
        'token': ''
    }
    usersDb.insert_one(person)
    userVideoPperation.insert_one({'pid': userId, 'likes': [], 'favorites': []})

    usersIcon.insert_one({'pid': userId, 'iconbase64': data['iconbase64']})

    return jsonify({'msg': 'OK'})

# 登入
@userApp.route('/login', methods=['POST'])
def login():

    data: dict = MapVer(request.get_json(),Bakedin(key='pwd', max=15, min=5, required=True), Bakedin(key='email', max=150, required=True))
    dtas = usersDb.find_one({'email':data['email']}, {'pid':1, 'pwd':1})
   
    if dtas is None:
        abort(makeResponse(-1, '邮箱错误'))

    if dtas['pwd'] != data['pwd']:
        abort(makeResponse(-2, '密码错误'))

    # 生成随机token
    infiId = dtas['pid']
    testStr = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    a_str = md5_string(f'nmslwocaonima{infiId}{time.time()}{testStr}')

    redis_conn.set(infiId, f'{a_str}', 54000)
    usersDb.update_one({'pid': dtas['pid']}, {'$set': {'token': a_str}})

    res = make_response({'code': 200,'msg': 'OK'})
    res.headers['Authorization'] = a_str
    return res

# 登出
@userApp.route('/logout', methods=['POST'])
def logout():
    userId = isUser(request)['pid']

    redis_conn.delete(userId)

    res = make_response({'msg': 'OK'})
    return res

# 修改密码
@userApp.route('/changepwd', methods=['POST'])
def changePwd():
    data: dict = MapVer(request.get_json(), 
                        Bakedin(key='email', max=150, required=True),
                        Bakedin(key='code', max=8, required=True),
                        Bakedin(key='newpwd', max=15, min=5, required=True)
                    )
    
    emaCode = redis_conn.get(data['email'])
    if emaCode != data['code']:
        abort(makeResponse(-1, '验证码错误'))

    usersDb.update_one({"email": data['email']}, {"$set": { "pwd": data['newpwd']}}, )

    return jsonify({'msg': 'OK'})

# 修改头像
@userApp.route('/changeicon', methods=['POST'])
def changeIcon():
    userId = isUser(request)['pid']
    data1: dict = MapVer(request.get_json(), 
                        Bakedin(key='iconbase64', max=10*1024, required=True))
    
    data = usersDb.find_one({'pid': userId}, {'pid': 1})
    if data is  None:
        abort(makeResponse(-1, '用户不存在'))
   
    if isImage(data1['iconbase64']) is False:
        abort(makeResponse(-3, '格式不正确'))
    
    usersIcon.update_one({'pid': userId}, {'$set': {'iconbase64': data1['iconbase64']}})

    return jsonify({'msg': 'OK'})

# 用户信息
@userApp.route('/userinfo', methods=['GET'])
def userInfo():
    userId = StrVer(data=request.args.get('id'), max=100, min=10)
    data = usersDb.find_one({'pid': userId}, {'pid': 1, 'name': 1, '_id': 0})
    if data is  None:
        abort(makeResponse(-1, '用户不存在'))

    icon = usersIcon.find_one({'pid': userId}, {'_id': 0})
    data['icon'] = icon
    return jsonify({'msg': 'OK', 'data': data})

#   
@userApp.route('/usermeinfo', methods=['GET'])
def userMeinfo():
    userId = isUser(request)['pid']
    data = usersDb.find_one({'pid': userId}, {'pid': 1, 'name': 1, '_id': 0})
    icon = usersIcon.find_one({'pid': userId}, {'_id': 0})
    data['icon'] = icon

    Pperations = userVideoPperation.find_one({'pid': userId}, {"likes": 1, 'favorites': 1, '_id': 0})
    data['likes'] = Pperations['likes']
    data['favorites'] = Pperations['favorites']

    videoId = []
    cursor = videoInfoDb.find({'userId': userId}, {'pid':1, '_id': 0})
    for result in cursor.limit(-1):
       videoId.append(result)
    
    data['videoIds'] = videoId
    
    return jsonify({'msg': 'OK', 'data': data})