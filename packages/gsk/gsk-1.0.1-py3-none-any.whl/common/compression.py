import zlib

class Compression:
    def __init__(self):
        pass
    def compress(self,data):
        return zlib.compress( data )

    def uncompress(self,data):
        return zlib.uncompress(data)