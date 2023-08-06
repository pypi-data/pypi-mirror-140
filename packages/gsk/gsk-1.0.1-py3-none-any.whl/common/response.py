# from django.http import HttpResponse
import base64
from django.http import HttpResponse,JsonResponse
from .json import JSON
class Response:
    def __init__(self):
        self.data = {}
        self.data["message"] = []
        self.data["type"] = "success"
        self.data["extra"] = []

    def __str__(self):
        return self.getJson()


    def message(self,type,text,code):
        m = {}
        m["type"] = type
        m["code"] = code
        m["text"] = text

        self.data["message"].append(m)
    def success(self,text):
        self.message("success",text,"")
        self.calcType()

    def error(self,text,code=""):
        self.message("error",text,code)


    def setExtra(self,extra,base64_enc=False):
        if base64_enc==False:
            self.data["extra"] = extra
        else:
            sample_string_bytes = extra.encode("utf8")
            base64_bytes = base64.b64encode(sample_string_bytes)
            base64_string = base64_bytes.decode("utf8")
            self.data["extra"] = base64_string

    def getExtra(self):
        return self.data["extra"]

    def calcType(self):
        type = "success"
        for i in list(range(len(self.data["message"]))):
            if self.data["message"][i]["type"]=="error":
                type = "error"

        self.data["type"] = type

    def getJson(self):
        return self.json()
        
    def json(self):
        self.calcType()
        return JSON.toString(self.data)

    def __str__(self):
        self.json()

    def __Json_Response__(self):
        return JsonResponse(self.data)

    def merge(self,resp):
        
        for msg in resp.data["message"]:
            self.message(msg["type"],msg["text"],msg["code"])
        self.calcType()

    def isError(self):
        self.calcType()
        if self.data["type"] == "error":
            return True
        else:
            return False

    def isSuccess(self):
        self.calcType()
        if self.data["type"] == "success":
            return True
        else:
            return False
            
    def toString(self):
        return self.json()
    # def HttpResponse(self):
    #     return HttpResponse(self.json())

    def getAllMessage(self):
        s = ""
        for msg in self.data["message"]:
            if msg["type"] == "success":
                s = s+msg["text"]+".<br>\n"
            else:
                s = s+msg["code"]+": "+msg["text"]+".<br>\n"
        return s
    
    def jsonResponse(self):
        return JsonResponse(self.data)