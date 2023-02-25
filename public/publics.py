
from models.models import usersDb


#smtp =>simple mail transfer protocol  简单邮件传输协议
import hashlib
import smtplib   
from configs.config import *
from email.message import EmailMessage
import ssl


from flask import Request, Response, make_response, request, abort
    


smtp=smtplib.SMTP('smtp.qq.com',25)


def sendemail(receiver: str, subject: str, body: str):
    context=ssl.create_default_context()
    
    msg=EmailMessage()
    msg['subject']=subject    #邮件主题
    msg['From']=EMAIL_ADDRESS #发送邮箱
    msg['To']=receiver        #接受邮箱
    msg.set_content(body)     #邮件内容

    with smtplib.SMTP_SSL("smtp.qq.com",465,context=context) as smtp:
        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
        smtp.send_message(msg)

# md5 加密
def md5_string(in_str):
    md5 = hashlib.md5()
    md5.update(in_str.encode("utf8"))
    result = md5.hexdigest()
    return result

# 生成错误响应数据
def makeResponse(code: int, err: str) -> Response:
    errres = make_response({'code': code, 'err': err})
    return errres

# 获取视频时长
import cv2
def getVideoDuration(filename):
  cap = cv2.VideoCapture(filename)
  if cap.isOpened():
    rate = cap.get(5)
    frame_num =cap.get(7)
    duration = frame_num/rate
    return duration
  return -1



def isUser(req: Request) -> dict:
  token = req.headers.get('Authorization')

  # token1 = StrVer(data=token, min=10, max=200) # 异常未处理，不知原因的错误
  # print('token'+token1)
  userData = usersDb.find_one({'token': token}, {'pid': 1, 'permissions': 1})
  if userData is None:
    abort(makeResponse(-1, 'Token不正确,无权限'))
  
  return userData


def isImage(base: str) -> bool:
   
    if base.split(';')[0] in ['data:image/png', 'data:image/jpg', 'data:image/jpge']:
        return True
    return False