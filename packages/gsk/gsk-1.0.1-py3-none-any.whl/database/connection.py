from .oracle import OracleDriver
from .sqlite import SQLite
class Connection:
    def __init__(self,parm=None):
        self.parm = parm
        self.handler = None
        self.upperCase=True
        self.open()
        self.exception = None
    def open(self):
        if self.parm != None:
            
            if self.parm["driver"] == "oracle":
                self.handler = OracleDriver(self.parm,self)
            elif self.parm["driver"] == "sqlite":
                self.handler = SQLite(self.parm,self)
        else:
            self.handler = OracleDriver(None,self)

    def commit(self):
        self.handler.commit()

    def close(self):
        self.handler.close()
    

    def rollback(self):
        self.handler.rollback()

    def select(self,sql):
        return self.handler.select(sql)

    def insert(self,sql,autoCommit=False):
        return self.handler.insert(sql,{},autoCommit)

    def update(self,sql,autoCommit=False):
        return self.handler.update(sql,{},autoCommit)

    def delete(self,sql,autoCommit=False):
        return self.handler.delete(sql,{},autoCommit)

    def makeInsertSql(self,dbtable,autoInsert,autoCommit):
        return self.handler.makeInsertSql(dbtable,autoInsert,autoCommit)

    def makeUpdateSql(self,dbtable,condition,autoInsert,autoCommit):
        return self.handler.makeUpdateSql(dbtable,condition,autoInsert,autoCommit)

    def makeSelectSql(self,dbtable,column,filter,order,ignoreCase=True):
        return self.handler.makeSelectSql(dbtable,column,filter,order,ignoreCase)