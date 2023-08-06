from django.http import JsonResponse
import json
import datetime
# from skg.common. import *

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class JSON:
    @staticmethod
    def parse(jsonStr):
        return json.loads(jsonStr)
    @staticmethod
    def dumps(jsonObj):
        
        return json.dumps(jsonObj ,default=myconverter)
    
    
class Response:
    def __init__(self):
        self.data = {"message":[],"type":"success","extra":None}
        
    def success(self,message):
        self.data["type"]="success"
        
        self.data["message"].append({"text":message,"code":""})
        
    def error(self,message,errorcode=""):
        self.data["type"]="error"
        self.data["message"].append({"text":message,"code":errorcode})
        
    def jsonResponse(self):
        return JsonResponse(self.data)
    def setExtra(self,data):
        self.data["extra"] = data
    
class DateFormats:
    
    @staticmethod
    def diff_in_ago(d):
        
        n = datetime.datetime.now()
        dt = n.replace(tzinfo=datetime.timezone.utc) - d.replace(tzinfo=datetime.timezone.utc)
        
        
        out = ""
        if d==n:
            return "Just now"
        
        
        if(dt.days!=0):
            out = str(dt.days)+" ago"
        elif (dt.seconds!=0):
            h = int(dt.seconds/3600)
            if h>0:
                out = str(h)+" hour ago"
            else:
                m = int(dt.seconds/60)
                if m >0:
                    out = str(m)+" minut ago"
                else:
                    out = "Just now"
        
        return out
        