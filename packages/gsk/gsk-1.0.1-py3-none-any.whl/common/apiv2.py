import hashlib
import requests
from .json import JSON

def APIV3_Call(request,endpoint,postParm={}):
    sr = request.scheme+"://"+request.META["HTTP_HOST"]+endpoint
    
    # print(request.COOKIES)
    postParm["csrfmiddlewaretoken"]=request.COOKIES["csrftoken"]
    try:
        r = requests.post(sr,data=postParm,cookies=request.COOKIES)
        # print(r.text)
        rx = JSON.fromString(str(r.text))
        return rx["extra"]
    except Exception as ex:
        print(ex)
        print("Server says")
        print(str(r.text))
        return []


def APIV2_Call(serverUrl,key,salt,parm):
    s = ""
    pList = {}
    parm["key"] = key
    # print(parm)
    for key in parm:
        if(parm[key]!=None):
            s = s + str(parm[key])
    s=s+salt
    r = hashlib.md5(s.encode())
    hash = r.hexdigest()
    pList["hash"] = hash
    
    for key in parm:
        # str = str + parm[key]
        pList[key] = parm[key]
    # print(s)
    
    resp = requests.post(serverUrl,pList, verify=False)
    return resp.text


class ApiConnection:
    def __init__(self,server,key,salt,appKey):
        self.server = server
        self.key = key
        self.salt = salt
        self.appKey = appKey

    def call(self,endPoint,parm):
        return  APIV2_Call(self.server+endPoint,self.key,self.salt,parm)