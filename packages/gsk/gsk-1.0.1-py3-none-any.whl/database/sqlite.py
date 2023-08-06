import cx_Oracle
import traceback
from cx_Oracle import InterfaceError,OperationalError
import sqlite3
from awgp.common.data import Recordset
#import cx_Oracle.InterfaceError
class SQLite:
    def __init__(self,parm=None):
        self.parm = parm
        self.conn = None
        if self.parm!=None:
            
            if "logService" in parm:
                self.logService = parm["logService"]
            else:
                self.logService = None
            if "server" in self.parm:
                self.connect()

    def close(self):
        self.conn.close()

    def connect(self):
        self.conn = sqlite3.connect(self.parm["server"])
    
    def dictfetchall(self,cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0].upper() for col in cursor.description]
        
        
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def select(self,sql):
        # try:
            
        #     cursor = self.conn.cursor(scrollable=True)
        #     cursor.execute(sql)
        #     columns = [col[0] for col in cursor.description]
        #     cursor.rowfactory = lambda *args: dict(zip(columns, args))
        #     return cursor
            
        # except OperationalError as ex:
        #     self.connect()
        #     if self.logService != None:
        #         self.logService.write("LOG","ERROR","HIGH","Oracle Database is not avilable. try to reconnect","cx_Oracle connection is not avilable for select query. try to reconnect that. sql query is "+sql)
        #     return None
        # except Exception as ex:
        #     return None

        with self.conn.cursor() as cursor:
            
            cursor.execute(sql)   
            
            r = Recordset()
            r.data = self.dictfetchall(cursor)
            return r
    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def insert(self,sql,parm,autoCommit=False):

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql,parm)
                if autoCommit==True:
                    self.conn.commit()
            except OperationalError as ex:
                self.connect()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","HIGH","Oracle Database is not avilable. try to reconnect","cx_Oracle connection is not avilable for insert query. try to reconnect that. traceback: "+exp)

                self.conn.rollback()
                return False
            except Exception as ex:
                self.conn.rollback()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","LOW","Runtime error: sql execution error","Runtime error: sql execution error traceback: "+exp)
        return True
       
    def update(self,sql,parm,autoCommit=False):

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql,parm)
                if autoCommit==True:
                    self.conn.commit()
            except OperationalError as ex:
                self.connect()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","HIGH","Oracle Database is not avilable. try to reconnect","cx_Oracle connection is not avilable for update query. try to reconnect that. traceback: "+exp)

                self.conn.rollback()
                return False
            except Exception as ex:
                self.conn.rollback()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","LOW","Runtime error: sql execution error","Runtime error: sql execution error traceback: "+exp)
        return True

    def delete(self,sql,parm,autoCommit=False):

        with self.conn.cursor() as cursor:
            try:
                
                cursor.execute(sql,parm)
                if autoCommit==True:
                    self.conn.commit()
            except OperationalError as ex:
                self.connect()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","HIGH","Oracle Database is not avilable. try to reconnect","cx_Oracle connection is not avilable for delete query. try to reconnect that. traceback: "+exp)

                self.conn.rollback()
                return False
            except Exception as ex:
                self.conn.rollback()
                exp = traceback.format_exc()
                if self.logService != None:
                    self.logService.write("LOG","ERROR","LOW","Runtime error: sql execution error","Runtime error: sql execution error traceback: "+exp)


        return True


    def makeInsertSql(self,dbtable,autoInsert=False,autoCommit=False):
        columns = dbtable.columns
        data = dbtable.data
        

        col = ""
        for c in columns:
            col = col + c.name + ","
        col = col.strip(",")
        sqls = []
        # print(type(data))
        if(type(data)==dict):
            data = [data]
        error = False
        for d in data:
            val = ""
            for dc in d:
                cl = dbtable.findColumn(dc)
                v = str(d[dc])
                if cl != None:
                    if cl.autonumber == True:
                        s = """select nvl(max("""+cl.name+"""),0) + 1 as total from """+dbtable.name
                        cc = dbtable.db.select(s)
                        rr = cc.fetchone()
                        v = str(rr["TOTAL"])
                    
                    fv = self.formatColumnValue(cl,fv) + " ,"

            val = val.strip(",")
            sql = "insert into "+dbtable.name+"("+col+") values("+val+")"
            if autoInsert == True:
                # print(sql)
                rs = self.insert(sql,[],autoCommit)
                if rs==False:
                    error = True
                sqls.append(rs)  
            else:  
                sqls.append(sql)
        if autoInsert == True:
            if error == True:
                return False
            else:
                return True
        else:
            return sqls
    
    def makeFilterCondition(self,dbtable,filter):
        
        w = ""
        if(type(filter)==dict):
            filter = [filter]
        for fl in filter:
            j = "and"
            c = ""
            vl = ""
            cn = "="
            ws = ""
            for f in fl:
                if f == "join":
                    j = fl[f]
                elif f == "cn":
                    cn = fl[f]
                else:
                    
                    vl = fl[f]
                    c = f
            

            cl = dbtable.findColumn(c)
            vl= self.formatColumnValue(cl,vl)
            if cn == "=":
                ws = c + " = " + vl 
            elif cn == "in":
                ws = c + " in( " + vl + ")"
            
            w = w + " "+ j + " " + ws
            print(w)           
        
        return w

    def formatColumnValue(self,column,value):
        cl = column
        v = value
        if cl.type == "CHAR":
            fv = "'"+ v +"'" 
        elif cl.type == "NUMBER":
            fv = v 
        elif cl.type == "FUNCTION":
            fv = v 
        elif cl.type == "DATE":
            if cl.valueFormat == "":
                fv = "to_date('"+ v +"')" 
            else:
                fv = "to_date('"+ v +"','"+cl.valueFormat+"')" 
        return fv

    def makeSelectSql(self,dbtable,column,filter,order):
        columns = dbtable.columns
        data = dbtable.data
        
        w = self.makeFilterCondition(dbtable,filter)
        f = ",".join(column)
        o = ",".join(order)
        sql = "select " + f + " from " + dbtable.name+ " where 1 = 1 " + w + " order by " + o
        return sql

    def makeUpdateSql(self,dbtable,filter,autoUpdate=False,autoCommit=False):
        columns = dbtable.columns
        data = dbtable.data
        
        w = self.makeFilterCondition(dbtable,filter)

        sqls = []
        # print(type(data))
        if(type(data)==dict):
            data = [data]
        error = False
        for d in data:
            val = ""
            con = ""
            for dc in d:

                cl = dbtable.findColumn(dc)
            
                v = str(d[dc])
                fv = v
                if cl != None:
                    if cl.autonumber == True:
                        s = """select nvl(max("""+cl.name+"""),0) + 1 as total from """+dbtable.name
                        cc = dbtable.db.select(s)
                        rr = cc.fetchone()
                        fv = str(rr["TOTAL"])

                    fv = self.formatColumnValue(cl,fv)
                    
                    val = val + dc + " = "+fv+","
            
            val = val.strip(",")
            
            sql = "update "+dbtable.name+" set " +val + " where " + w
            if autoUpdate == True:
                # print(sql)
                rs = self.update(sql,[],autoCommit)
                if rs==False:
                    error = True
                sqls.append(rs)  
            else:  
                sqls.append(sql)
        if autoUpdate == True:
            if error == True:
                return False
            else:
                return True
        else:
            return sqls