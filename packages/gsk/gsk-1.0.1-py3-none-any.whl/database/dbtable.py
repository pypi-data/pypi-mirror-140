from awgp.common.data import Recordset
from awgp.django.database import DB

class DBTable(Recordset):
    def __init__(self,name,db=None):
        super().__init__()
        self.name = name
        if db==None:
            db1 = DB("default")
            db = db1.toConnection()

        self.db = db
        
    def insert(self,autoInsert=False,autoCommit=False):
        return self.db.makeInsertSql(self,autoInsert,autoCommit)
        
    def update(self,condition,autoUpdate=False,autoCommit=False):
        return self.db.makeUpdateSql(self,condition,autoUpdate,autoCommit)
    
    def filter(self,col,condition,order,ignoreCase=True):
        return self.db.makeSelectSql(self,col,condition,order,ignoreCase)