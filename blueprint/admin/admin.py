
from flask import Blueprint, abort, request, jsonify, send_from_directory


from public.publics import *
from models.models import *
from verification.verifications import *

adminApp = Blueprint('adminApp', __name__, url_prefix='/nmsldeadminhoutaiguanli')

def isAdmin(req) -> dict:
    userData = isUser(req)
    if userData['permissions'] != 'Admin':
        abort(makeResponse(-1, f'用户无权限')) 
    return userData['pid']

# 操作用户
@adminApp.route('/reviseuser', methods=['GET'])
def reviseuser():
    userId = isAdmin(request)
    revisData = request.args
    setData = []
    for i,j in revisData.items():
        if i not in ['name','pwd', 'email', 'time', 'permissions']:
            abort(makeResponse(-1, f'参数错误')) 
        setData.append({i: j})

    usersDb.update_one({'pid':userId}, {'$set': setData})
    return jsonify({'msg': 'Ok'})


@adminApp.route('/revisevideo', methods=['POST'])
def revisevideo():
    isAdmin(request)
    revisData = request.args
    setData = []
    
    for i,j in revisData.items():
        if i == 'userid':
            
            continue
        if i not in ['name','pwd', 'email', 'time', 'permissions']:
            abort(makeResponse(-1, f'参数错误')) 
        setData.append({i: j})

    return jsonify({'msg': 'Ok'})

@adminApp.route('/delete', methods=['POST'])
def delete():  
    isAdmin(request)
    pid = request.args.get('id')
    types = request.args.get('types')
    if types == 'user':
        usersDb.delete_one({'pid': pid})
        userVideoPperation.delete_one({'pid': pid})
        videoCommentsDb.update_many({{}, {'$unset': {pid: 1}}})
    if types == 'video':
        videoInfoDb.delete_one({'pid': pid})
        videoVarietyNumDb.delete_one({'pid': pid})
        videoCommentsDb.delete_one({'pid': pid})

    return jsonify({'msg': 'Ok'})

@adminApp.route('/send', methods=['GET'])
def send():
    isAdmin(request)
    types = request.args.get('types')
    
   
    if types == 'user':
        rerp = []
        # 
        data = usersDb.find({},{'_id': 0})
        
        for result in data.limit(0):
            
            rerp.append(result)
        
        return jsonify({'msg': 'Ok', 'data': rerp}) 
    if types == 'video':
        
        data = videoInfoDb.find({}, {'_id': 0})
        
        return jsonify({'msg': 'Ok', 'data': list(data)}) 