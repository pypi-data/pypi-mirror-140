import io
from datetime import datetime
import os
class LogWriter:
    def __init__(self,name,path="./"):
        self.name = name
        self.filename = path+name.replace(" ","_")+"log"
        

    def write(self,type,message):
        content = str(datetime.now())+"|"+str(type)+"|"+str(message)
        print(content)
        file = open(self.filename,"a+")
        file.write(content+"\n")
        file.close()
        
        
class TraceFile:
    def __init__(self,name):
        self.name = name
        self.data = {}
        # print(name)
        if os.path.isfile(name)==True:
            f = open(name,"r")
            
            d= f.read()
            # print(name)
            dd = d.split("\n")
            
            for d in dd:
                # print(d)
                if "Request:" in d:
                    self.data["Request"]=d.split("Request:")[1]
                elif "Request HEADERS:" in d:
                    self.data["HEADERS"]=d.split("Request HEADERS:")[1]
                elif "Request COOKIE:" in d:
                    self.data["COOKIE"]=d.split("Request COOKIE:")[1]
                elif "Request GET:" in d:
                    self.data["GET"]=d.split("Request GET:")[1]
                elif "Request POST:" in d:
                    self.data["POST"]=d.split("Request POST:")[1]
                    self.data["POST"] = self.data["POST"].split("Request FILES:")[0]
                d= f.readline()
            f.close()
        # print(self.data)
            