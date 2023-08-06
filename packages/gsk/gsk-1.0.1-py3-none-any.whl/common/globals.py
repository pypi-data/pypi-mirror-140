class GlobalData():
    def __init__(self):
        self.data = {}

    def set(self,name,value):
        self.data[name] = value

    def get(self,name):
        return self.data[name]

GLOBALS = GlobalData()