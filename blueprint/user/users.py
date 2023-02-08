import random
import string
import time
import uuid
from bson.objectid import ObjectId

from flask import Blueprint, request, jsonify, make_response
from public.publics import isUser, md5_string

from verification.verifications import *
from models.models import *

userApp = Blueprint('userApp', __name__, url_prefix='/users')

# 注册
@userApp.route('/register', methods=['POST'])
def register():
    
    data: dict = MapVer(request.get_json(), 
                        Bakedin(key='name', max=15, min=3, required=True), 
                        Bakedin(key='pwd', max=15, min=5, required=True), 
                        Bakedin(key='email', max=150, required=True),
                        Bakedin(key='code', max=8, required=True),
                        Bakedin(key='iconbase64', max=500*1024, required=True))
    
    emaCode = redis_conn.get(data['email'])
    if emaCode != data['code']:
        abort(makeResponse(-1, f'验证码错误'))

    dtas = usersDb.find_one({'$or': [{'name':data['name']}, {'email': data['email']}]})
    if  dtas is not None:
        if dtas['name'] == data['name']:
            abort(makeResponse(-2, '用户名称已存在'))
        if dtas['email'] == data['email']:
            abort(makeResponse(-3, '邮箱已被使用'))

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

    res = make_response({'msg': 'OK'})
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


@userApp.route('/changename', methods=['GET'])
def changeName():
    userId = isUser(request)['pid']
    
    newName = StrVer(data=request.args.get('newname'), max=15, min=3)
    data = usersDb.find_one({'name': newName})
    if data is not None:
         abort(makeResponse(-1, '用户名已存在'))
    usersDb.update_one({'pid': userId}, {'$set': {'name': newName}})

    return jsonify({'msg': 'OK'})