import re

from flask import abort

from public.publics import makeResponse

# 校验字符串
def StrVer(*, data: str, max: int = None, min: int = None, restr = None) -> str:
    if data is None or len(data) == 0:
        return data

    if max != None:
        if len(data) > max:
            abort(makeResponse(-11, f'{data}:参数超过最长限制长度-参数长度:{len(data)}-限制长度:{max}'))

    
    if min != None:
        if len(data) < min:
            abort(makeResponse(-11,f'{data}:参数小于最小限制长度-参数长度:{len(data)}-限制长度:{min}'))
            
    
    if restr != None:
        pattern = re.compile(restr)
        result = pattern.findall(data)
        if len(result) != 0:
            abort(makeResponse(-33, f'{data}:参数违法:{data}'))
           
    
    return data

def IntVer(*, data: int, max: int = None, min: int = None,) -> int:
    if  data is None :
        return data

    
    if len(data) > max:
        abort(makeResponse(-11, f'{data}:参数大于限制-参数大小:{len(data)}-限制大小:{max}'))

    if min != None:
        if len(data) < min:
            abort(makeResponse(-11,f'{data}:参数小于限制-参数大小:{len(data)}-限制大小:{min}'))
           

def Bakedin(*, key: str, max=None, min=None, required=False, restr=None) -> str:
    return {'key': key, 'max': max, 'min': min, 'required': required, 'restr': restr}

# 校验dict
def MapVer(data: dict, *args) -> dict:
    for i in args:
        

        # 数据是否可忽略
        if i['required']:
            if not i['key'] in data:
                
                keys = i['key']
                abort(makeResponse(-11, f'未携带参数:{keys}'))

            if isinstance(data[i['key']], int):
                if data[i['key']] is None:
                    abort(makeResponse(-22, f'参数不能为空'))

            if data[i['key']] == None or len(data[i['key']]) == 0:
                    abort(makeResponse(-22, f'参数不能为空'))

        if data[i['key']] == None or len(data[i['key']]) == 0:
            continue
        
        if isinstance(data[i['key']], int):
            IntVer(data = data[i['key']], max=i['max'], min=i['min'])
            continue

        StrVer(data = data[i['key']], max=i['max'], min=i['min'], restr=i['restr'])
    return data
        
