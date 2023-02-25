
import os
from flask import Blueprint, abort, request, jsonify, send_from_directory
from configs.config import VIDEOPATH


from public.publics import isUser, makeResponse
from models.models import usersDb, videoInfoDb, userVideoPperation, videoCommentsDb, videoVarietyNumDb


adminApp = Blueprint('adminApp', __name__, url_prefix='/nmsldeadminhoutaiguanli')

def isAdmin(req) -> dict:
    userData = isUser(req)
    if userData['permissions'] != 'Admin':
        abort(makeResponse(-1, f'用户无权限')) 
    return userData['pid']

# 操作用户
@adminApp.route('/reviseuser', methods=['GET'])
def reviseuser():
    isAdmin(request)
    revisData = request.args
    setData = {}
    for i,j in revisData.items():
        if i not in ['name','pwd', 'email',  'permissions']:
            continue
        if j is None or len(j) == 0:
            continue
        setData[i] = j
    
    usersDb.update_one({'pid':revisData['id']}, {'$set': setData})
    return jsonify({'msg': 'Ok'})


@adminApp.route('/revisevideo', methods=['POST'])
def revisevideo():
    isAdmin(request)
    revisData = request.args
    setData = {}
    
    for i,j in revisData.items():
        if i == 'userid':
            
            continue
        if i not in ['title','label', 'synopsis']:
            continue 
        if j is None or len(j) == 0:
            continue
        setData[i] = j
    videoInfoDb.update_one({'pid':revisData['id']}, {'$set': setData})
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
        videoInfo = videoInfoDb.find_one({'pid':pid}, {'pid': 1, "userId": 1})
        if videoInfo is None:
            abort(makeResponse(-1, f'无数据'))

        videoId = videoInfo['pid']
        userId = videoInfo['userId']
        path = f'{VIDEOPATH}/{userId}/{videoId}'
        filelist = os.listdir(path)
        for i in filelist:
            os.remove(f'{path}/{i}')
        os.rmdir(path)
        videoInfoDb.delete_one({'pid': pid})
        videoVarietyNumDb.delete_one({'pid': pid})
        videoCommentsDb.delete_one({'pid': pid})
        
    return jsonify({'msg': 'Ok'})

# 发送全部用户或视频
@adminApp.route('/send', methods=['GET'])
def send():
    isAdmin(request)
    types = request.args.get('types')
    revisData = request.args
    setData = {}
    setDataList = []
    for i,j in revisData.items():
       
        if i in ['current', 'pageSize', 'types']:
            continue
        if j is None or len(j) == 0:
            continue
        if i in ['isReview']:
            
            isReview = False
            if j is '1':
                isReview = True
            setDataList.append({i: isReview})
            continue
        setDataList.append({i: {'$regex': j}})
    if len(setDataList) != 0:
        setData = {'$and': setDataList}
    
    if types == 'user':
       
        data = usersDb.find(setData,{'_id': 0})
    
        return jsonify({'msg': 'Ok', 'data': list(data)}) 
    if types == 'video':
        
        data = videoInfoDb.find(setData, {'_id': 0})
        
        return jsonify({'msg': 'Ok', 'data': list(data)}) 