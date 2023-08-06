from awgp.common.compression import Compression
class DataBox:
    def __init__(self):
        self.id = ""
        self.version = ""
        self.data = {}
        self.time = ""
        self.enc = ""
        self.keylist = ""

    def toString(self):
        temp = {}
        temp["id"] = self.id
        temp["version"] = self.version
        temp["data"] = self.data
        temp["time"] = self.time
        temp["enc"] = self.enc
        temp["keylist"] = self.keylist

    def dataProcessor(self,data):
        c = Compression()
        return c.compress(data)