import os
import time
import uuid
from flask import Blueprint, abort, request, jsonify, send_from_directory
from bson.objectid import ObjectId


from public.publics import makeResponse, isUser, getVideoDuration
from models.models import videoInfoDb, videoVarietyNumDb
from verification.verifications import StrVer, MapVer, Bakedin
from configs.config import VIDEOPATH

videoApp = Blueprint('videoApp', __name__, url_prefix='/videos')

# 上传视频
@videoApp.route('/uploadvideo', methods=['POST'])
def uploadVideo():

    title = StrVer(data=request.form.get('title'), min=3, max=40) # 标题

    label = request.form.get('label') # 标签
    for j in label.split(','):
        StrVer(data=j, min=2, max=6)

    synopsis = StrVer(data=request.form.get('synopsis'), min=2, max=150)  # 简介   

    cover = request.files.get('videoscover') # 视频封面
    if cover is None:
        abort(makeResponse(-1, '参数videoscover为空'))
        
    if cover.content_length > 1*1024*1024:
        abort(makeResponse(-1, '图片过大'))

    fil = request.files.getlist('videos') # 视频本体
    if fil is None:
        abort(makeResponse(-2, '参数videos为空'))

    
    userId = isUser(request)['pid']

    videoId = uuid.uuid5(uuid.uuid4(), uuid.uuid4().hex).hex[0: 24]

    num = 0
    durationAll = 0
    videoPathList = []
    for i in fil:
        
        filenameList = i.filename.split('.')
        if filenameList[-1] != 'mp4':
            abort(makeResponse(-3, '格式错误'))

        path = f'{VIDEOPATH}/{userId}/{videoId}'
        if os.path.exists(path) is False:
            os.makedirs(path)

        url = f'{VIDEOPATH}/{userId}/{videoId}/{videoId}-{num}.mp4'
        
        i.save(url)

        duration = getVideoDuration(url)
        if duration == -1:
            abort(makeResponse(-4, '参数格式异常'))
        durationAll += duration
        videoPathList.append({'num': num, 'videoTime': duration, 'videosPath': f'../video/{userId}/{videoId}', 'videoName': f'{videoId}-{num}.mp4'})
        num += 1
    
    coverId = uuid.uuid4().hex
    coverPath = f'{VIDEOPATH}/{userId}/{videoId}/{coverId}.jpg'
    coverUrl = f'/pub/sendimage?userid={userId}&videoid={videoId}&name={coverId}.jpg'
    cover.save(coverPath)

   

    videoCreateTime = time.time()  
    videoInfoPerson = {
        'pid': videoId,
        'userId': userId,
        'title': title, # 标题
        'label': label, # 标签
        'synopsis': synopsis, # 简介   
        'episodes': num, # 集数 
        'coverPath': coverUrl,  # 视频封面
        'videoPathData':videoPathList,
        'videoCreateTime': videoCreateTime,
        'videoTime': durationAll,
        'isReview': False, # 视频审核
    }

    videoInfoDb.insert_one(videoInfoPerson)

    
    # 观看，点赞，收藏数据库
    videoVarietyNumDbPerson = {'pid': videoId, 'views': 0, 'Likes': 0, 'Favorites': 0, 'Comments': 0}
    videoVarietyNumDb.insert_one(videoVarietyNumDbPerson)

    return jsonify({'msg': 'OK'})

# 修改视频
@videoApp.route('/modifyvideo', methods=['POST'])
def modifyVideo():

    userId = isUser(request)['pid']

    videoId = StrVer(data=request.form.get('videoid'),  max=60) # 

    videoInfo = videoInfoDb.find_one({'$and': [{'pid': videoId}, {'userId': userId}]})
    if videoInfo is None:
        abort(makeResponse(-1, f'无权修改'))

    title = StrVer(data=request.form.get('title', default=''),  max=40) # 标题

    label = request.form.get('label', default='') # 标签
    

    synopsis = StrVer(data=request.form.get('synopsis', default=''), min=2, max=150)  # 简介   

    cover = request.files.get('videoscover', default='') # 视频封面
    
    updataInfo = {}
    
    if title is not None and len(title) != 0:
        
        updataInfo['title'] = title
        
        
    if label is not None and len(label) != 0:

        updataInfo['label'] = label
    
    if synopsis is not None and len(synopsis) != 0:
        
        updataInfo['synopsis'] = synopsis

    
    if not isinstance(cover, str):
        
        data = videoInfo['coverPath'].split('=')
        userId: str = data[1].split('&')[0]
        videoId: str = data[2].split('&')[0]
        coverPath = f'{VIDEOPATH}/{userId}/{videoId}/{data[-1]}'
        cover.save(coverPath)

    videoInfoDb.update_one({'pid': videoId}, {'$set': updataInfo})
    
   
    return jsonify({'msg': 'OK'})

# 删除视频
@videoApp.route('/deletevideo', methods=['POST'])
def deleteVideo():
    userId = isUser(request)['pid']
    data: dict = MapVer(request.get_json(),Bakedin(key='videoid',max=60, required=True))
    
    videoInfo = videoInfoDb.find_one({'$and': [{'pid': data['videoid']}, {'userId': userId}]}, {'pid': 1})
    if videoInfo is None:
        abort(makeResponse(-1, f'无权修改'))

    videoId = videoInfo['pid']
    path = f'{VIDEOPATH}/{userId}/{videoId}'
    filelist = os.listdir(path)
    for i in filelist:
        os.remove(f'{path}/{i}')
    os.rmdir(path)
    
    videoInfoDb.delete_one({'pid': data['videoid']})
    videoVarietyNumDb.delete_one({'pid': data['videoid']})

    return jsonify({'msg': 'OK'})


# 发送视频
@videoApp.route('/sendvideo', methods=['GET'])
def sendVideo():
    videoid = StrVer(data=request.args.get('videoid'), min=1)
    num = StrVer(data=request.args.get('num'), min=1)
    videoInfo = videoInfoDb.find_one({'pid': videoid})
    
    
    if videoInfo is None:
        abort(makeResponse(-1, f'视频不存在'))
   
    videoVarietyNumDb.update_one({'pid': videoid}, {'$inc': {'views': 1}})

    for i in videoInfo['videoPathData']:
        if i['num'] == int(num):
            
            return send_from_directory(i['videosPath'], i['videoName'], as_attachment=True)
            # 限制传输大小
            # filename = i['videoName']
            # response = Response(send_file(i['videosPath'], filename), content_type='video/mp4')
            # response.headers['Content-Type'] = 'video/mp4'
            # response.headers["Content-disposition"] = f'attachment; filename={filename}'   # 如果不加上这行代码，导致下图的问题
            # return response
    
    abort(makeResponse(-1, '发生错误请检查'))

# 切片发送
def send_file(videosPath, videoName):
        store_path = os.path.join(videosPath,videoName)
        with open(store_path, 'rb') as targetfile:
            while 1:
                data = targetfile.read(5 * 1024 * 1024)   # 每次读取5MB (可用限速)
                if not data:
                    break
                yield data


@videoApp.route('/carouselvideo')
def carouselVideo():
    pass

# 视频搜索
@videoApp.route('/searchvideo', methods=['GET'])
def searchVideo():
    search = StrVer(data=request.args.get('search'), min=1)
    searchData = videoInfoDb.find({'$and': [{'isReview': True}, {'$or': [{'title':{'$regex': search}}, {'label':{'$regex': search}}]}]})
    
    dataList = []
    for result in searchData.limit(-1):
        del result['videoPathData']
        del result['isReview']
        result['pid'] = result['pid']
        dataList.append(result)
  
    return jsonify({'msg': dataList})