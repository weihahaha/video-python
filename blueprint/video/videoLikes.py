
from flask import Blueprint, request, jsonify

from public.publics import *
from models.models import *
from verification.verifications import *

videoLikesApp = Blueprint('videoLikesApp', __name__, url_prefix='/likes')

# 视频点赞
@videoLikesApp.route('/videolikes', methods=['GET'])
def videoLikes():
    userId =isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=10, max=100)
    videoLikesList = userVideoPperation.find_one({ 'pid': userId }, {'likes': 1})
   
    for i in videoLikesList['likes']:
        if i == videoId:
            abort(makeResponse(-1, '用户已点赞'))

    try:
        videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Likes': 1}})
        userVideoPperation.update_one({ 'pid':userId },{ '$push': { 'likes':  videoId}} )
    except:
        abort(makeResponse(-2, '参数异常'))

    return jsonify({'msg': 'OK'})

# 视频取消点赞
@videoLikesApp.route('/videolikescancel', methods=['GET'])
def videoLikesCancel():
    userId = isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=1, max=100)
    videoLikesList = userVideoPperation.find_one({ 'pid': userId }, {'likes': 1})
    likesList = videoLikesList['likes']

    if len(likesList) == 0:
        abort(makeResponse(-1, '用户未点赞'))

    for j in likesList:
        if j != videoId:
            abort(makeResponse(-1, '用户未点赞'))
        else:
            userVideoPperation.update_one({ 'pid': userId }, {'$pull': {'likes':  j}} )

    try:
        videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Likes': -1}})
    except:
        abort(makeResponse(-2, '参数异常'))  

    return jsonify({'msg': 'OK'})

# 用户点赞数
@videoLikesApp.route('/videolikesdata', methods=['GET'])
def videoFavoritesData():
    userId = isUser(request)['pid']
    videoLikesList = userVideoPperation.find_one({ 'pid': userId }, {'likes': 1})
    likesList = videoLikesList['likes']
    if len(likesList) == 0:
        abort(makeResponse(-1, '用户无点赞'))

    return jsonify({'msg': likesList})

# 用户是否点赞
@videoLikesApp.route('/videoislikes', methods=['GET'])
def videoislikes():
    userId = isUser(request)['pid']
    videoid = StrVer(data=request.args.get('videoid'), min=10) 
    videoLikesList = userVideoPperation.find_one({ 'pid': userId }, {'likes': 1, '_id':0})
    if len(videoLikesList) == 0:
        abort(makeResponse(-1, '用户无收藏'))
    
    for i in videoLikesList['likes']:
        if i == videoid:
            return  jsonify({'msg': 'OK', 'is': True})

    return  jsonify({'msg': 'OK', 'is': False})