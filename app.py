from flask import Flask, abort , request
from gevent.pywsgi  import  WSGIServer
from gevent import monkey

monkey.patch_all()
from public.publics import makeResponse
from verification.verifications import StrVer

from blueprint.user.users import userApp
from blueprint.video.videos import videoApp
from blueprint.video.videoLikes import videoLikesApp
from blueprint.video.videoFavorites import videoFavoritesApp
from blueprint.video.videoComments import videoCommentsApp
from blueprint.admin.admin import adminApp
from blueprint.pub.pubs import pubApp

from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

app.register_blueprint(userApp)
app.register_blueprint(videoApp)
app.register_blueprint(videoLikesApp)
app.register_blueprint(videoFavoritesApp)
app.register_blueprint(videoCommentsApp)
app.register_blueprint(pubApp)
app.register_blueprint(adminApp)


@app.before_request
def br():
   isTokenPath = ['/users/logout',  '/users/changename',
                  '/videos/uploadvideo','/videos/modifyvideo', '/videos/deletevideo',
                  '/likes/videolikes', '/likes/videoLikesCancel','/likes/videolikesdata','/likes/videoislikes',
                  '/favorites/videofavoritescancel','/favorites/videofavorites','/favorites/videofavoritesdata','/favorites/videoisfavorites',
                  '/comments/videocomments','/comments/videocommentscancel']
   if request.path in isTokenPath:
      token = StrVer(data=request.headers.get('Authorization'), min=10, max=200)
      if token is None:
         abort(makeResponse(-1, '请登入'))
   
   
   

# 异常处理
@app.errorhandler(Exception)
def errh(error):
   print(error)
   if error != None: 
      return error

if __name__ == '__main__':
   app.debug = True
   server = WSGIServer(('0.0.0.0',3399), app)
   print(
   '''
    ____  _  _   ___  ___  ____  ____  ____ 
   / ___)/ )( \ / __)/ __)(  __)/ ___)/ ___)
   \___ \) \/ (( (__( (__  ) _) \___ \\___ \\
   (____/\____/ \___)\___)(____)(____/(____/
   ''')
   
   server.serve_forever()