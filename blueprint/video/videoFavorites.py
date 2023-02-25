from aiohttp import request
from bson import ObjectId
from flask import Blueprint, abort, jsonify

from public.publics import isUser,  makeResponse
from models.models import userVideoPperation, videoVarietyNumDb
from verification.verifications import StrVer


videoFavoritesApp = Blueprint('videoFavoritesApp', __name__, url_prefix='/favorites')

# 点赞
@videoFavoritesApp.route('/videofavorites', methods=['GET'])
def videoFavorites():
    userId = isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=10, max=100)
    videoFavoritesList = userVideoPperation.find_one({ 'pid': userId }, {'favorites': 1})
    
    for i in videoFavoritesList['favorites']:
        if i == videoId:
            abort(makeResponse(-1, '用户已收藏'))

    try:
        videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Favorites': 1}})
        userVideoPperation.update_one({ 'pid': userId },{ '$push': { 'favorites':  videoId}} )
    except:
        abort(makeResponse(-2, '参数异常'))

    return jsonify({'msg': 'OK'})

# 取消点赞
@videoFavoritesApp.route('/videofavoritescancel', methods=['GET'])
def videoFavoritesCancel():
    userId = isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=1, max=100)
    videoFavoritesList = userVideoPperation.find_one({ 'pid': userId }, {'favorites': 1})
    favoritesList = videoFavoritesList['favorites']
    
    print(videoFavoritesList)
    if len(favoritesList) == 0:
        abort(makeResponse(-1, '用户收藏为空'))

    for j in favoritesList:
        if j != videoId:
            abort(makeResponse(-1, '用户未收藏'))
        else:
            userVideoPperation.update_one({ 'pid': userId }, {'$pull': {'favorites':  j}} )

    try:
        videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Favorites': -1}})

    except:
        abort(makeResponse(-2, '参数异常'))  

    return jsonify({'msg': 'OK'})


# 用户总收藏
@videoFavoritesApp.route('/videofavoritesdata', methods=['GET'])
def videoFavoritesData():
    userId = str(isUser(request)['pid'])
    videoFavoritesList = userVideoPperation.find_one({ 'pid': userId }, {'favorites': 1})
    favoritesList = videoFavoritesList['favorites']
    if len(favoritesList) == 0:
        abort(makeResponse(-1, '用户无收藏'))

    return jsonify({'msg': favoritesList})

# 用户是否收藏
@videoFavoritesApp.route('/videoisfavorites', methods=['GET'])
def videoIsFavorites():
    userId = isUser(request)['pid']
    videoid = StrVer(request.args.get('videoid'), min=10) 
    videofavoritesList = userVideoPperation.find_one({ 'pid': userId }, {'favorites': 1})
    if len(videofavoritesList) == 0:
        abort(makeResponse(-1, '用户无收藏'))

    for i in videofavoritesList['favorites']:
        if i == videoid:
            return  jsonify({'msg': 'OK', 'is': True})

    return  jsonify({'msg': 'OK', 'is': False})