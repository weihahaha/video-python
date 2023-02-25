import random
import string
from flask import Blueprint, abort, request, jsonify, send_from_directory
from public.publics import sendemail
from models.models import *

from verification.verifications import MapVer, Bakedin, makeResponse
pubApp = Blueprint('pubApp', __name__, url_prefix='/pub')

@pubApp.route('/sendcode',  methods=['POST'])
def sendcode():
    data: dict = MapVer(request.get_json(), Bakedin(key='email', max=150, required=True))

   
    if redis_conn.exists(data['email']):
          abort(makeResponse(-1, '验证码以发放请,等待5分钟后尝试'))
        

    a_str = ''.join(random.sample(string.ascii_letters + string.digits, 7))
    sendemail(data['email'], "验证码", f'验证码为：{a_str}')
    redis_conn.set(data['email'], a_str, ex=300, nx=True)
    return jsonify({'msg': '验证码发送成功OK'})


@pubApp.route('/sendimage',  methods=['POST'])
def sendimage():
     userid = request.args.get('userid')
     videoid = request.args.get('videoid')
     imageName = request.args.get('name')
     path = f'../video/{userid}/{videoid}'
     return send_from_directory(path, imageName, as_attachment=True)