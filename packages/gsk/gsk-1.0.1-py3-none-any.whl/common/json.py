import simplejson as json
import datetime
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

class JSON:
    
    def __init__(self):
        self.data = []

    def fromString(string=""):
        return json.loads(string)

    def toString(data=[]):
        return json.dumps(data,default=myconverter)

    def dumps(data):
        return json.dumps(data,default=myconverter)

JSON.fromString = staticmethod(JSON.fromString)
JSON.toString = staticmethod(JSON.toString)
JSON.dumps = staticmethod(JSON.dumps)