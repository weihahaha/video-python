import time
from bson import ObjectId
from flask import Blueprint, jsonify

from public.publics import *
from models.models import *
from verification.verifications import *


videoCommentsApp = Blueprint('videoCommentsApp', __name__, url_prefix='/comments')

# 添加评论
@videoCommentsApp.route('/videocomments', methods=['GET'])
def videocomments():
    userId = isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=10, max=100)
    comments = StrVer(data=request.args.get('comments'), min=2, max=100)
    videoInfo = videoInfoDb.find_one({'pid': videoId}, {'pid': 1})

    if videoInfo is None:
        abort(makeResponse(-1, '视频不存在'))
    
    commentsdata = {
        'time': time.time(),
        'text': comments
    }
    try:
        videoCommentsDb.insert_one({'pid': videoId, userId: [commentsdata]})
    except:
        videoCommentsDb.update_one({'pid': videoId}, {'$push': {userId: commentsdata}})
    videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Comments': 1}})
    return jsonify({'msg': 'OK'})
    
# 删除 评论
@videoCommentsApp.route('/videocommentscancel', methods=['GET'])
def videocommentscancel():
    userId = isUser(request)['pid']
    videoId = StrVer(data=request.args.get('videoid'), min=10, max=100)
    comments = StrVer(data=request.args.get('comments'), min=2, max=100)
    
    videoComments: dict = videoCommentsDb.find_one({'pid': videoId}, {'_id': 0,'pid': 0})
    
    
    if videoComments is None:
        abort(makeResponse(-1, '视频不存在'))
    else:
        videoCommentsDb.update_one({'pid' : videoId},{'$pull': {userId: {'text': comments}}})
        videoVarietyNumDb.update_one({'pid': videoId}, {'$inc': {'Comments': -1}})
        
    return jsonify({'msg': 'OK'})

# 发送视频评论
@videoCommentsApp.route('/videocommentsdata', methods=['GET'])
def videocommentsdata():
    videoId = StrVer(data=request.args.get('videoid'), min=10, max=100)
    videoComments = videoCommentsDb.find({ 'pid': videoId}, {'pid':0, '_id':0})

    dataList = []
    for result in videoComments.limit(-1):

        dataList.append(result)

    return jsonify({'msg': 'OK', 'data': dataList})
    