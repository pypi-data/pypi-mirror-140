from .http import HttpRequest
import requests
from datetime import datetime
from awgp.common.utils import uniqid
import base64
class LogService:
    
    def __init__(self,application,server="http://logs.awgp.in:8002"):
        self.server = server
        self.application = application
        self.writeLocal = False
        self.writeRemote = True
        self.logLevel = 1
        self.echo = False
        

    def write(self,channel,type,priority,title,text="NA",level=1):
        data = {
            "channel":channel,
            "type":type,
            "priority":priority,
            "title":title,
            "text":text,
            "application":self.application
        }
        if level >= self.logLevel:
            if self.writeRemote ==  True:
                requests.post(self.server+"/api/write",data)

            dt = str(datetime.now())+"|"+self.application+"|"+channel+"|"+type+"|"+priority+"|"+title
            if self.writeLocal == True:
                file = open("logService.log","a+")
                file.write(dt+"\n")
                file.close()

            if self.echo == True:
                print(dt)

        return True




        

class SMSService:
    def __init__(self,key,secret):
        self.key = key
        self.secret = secret

    def send(self,mobile,message):
        id = uniqid()
        message = str(base64.b64encode(bytes(message,"utf-8")),"utf-8")
        endPoint = "http://smsrelay.awgp.in/client.php?auth="+str(self.key)+"&request_id="+str(id)+"&mobile="+str(mobile)+"&text="+str(message)+"&encr=true&enc=false"
        print(endPoint)
        r = requests.get(endPoint)
        print(r.content)

        
        