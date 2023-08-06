from pymongo import MongoClient
class MongoDb():
    def __init__(self,server,port,username,password,database,authDb="admin"):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.authDb = authDb
        self.database = database
        CONNECTION_STRING = f"mongodb://{username}:{password}@{server}:{port}/{authDb}"
        
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client[database]
        
    def getCollection(self,collection):
        return self.db[collection]
    
    def insertMeny(self,collection,data):
        c = self.getCollection(collection)
        return c.insert_many(data)
    def insert(self,collection,data):
        c = self.getCollection(collection)
        return c.insert_one(data)
    
    def find(self,collection,query={}):
        c = self.getCollection(collection)
            
        return c.find(query)