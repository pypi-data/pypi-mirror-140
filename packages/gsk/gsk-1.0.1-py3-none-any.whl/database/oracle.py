import cx_Oracle
import traceback
from cx_Oracle import InterfaceError,OperationalError
from awgp.common.data import Recordset
#import cx_Oracle.InterfaceError
class OracleDriver:
    def __init__(self,parm=None,connection=None):
        self.parm = parm
        self.handler = connection
        if self.parm!=None:
            
            if "logService" in parm:
                self.logService = parm["logService"]
            else:
                self.logService = None
            if "server" in self.parm:
                self.connect()

            # self.connect()

    def close(self):
        self.conn.close()


    def dictfetchall(self,cursor):
        "Return all rows from a cursor as a dict"
        # print("AS")
        # print(self.handler.upperCase)
        if self.handler.upperCase==True:
            
            columns = [col[0].upper() for col in cursor.description]
        else:
            
            columns = [col[0].lower() for col in cursor.description]
        # print(columns)
        def test(row):
            index = 0
            out = []
            for i in row:
                if type(i) == cx_Oracle.LOB:
                    out.append(i.read())
                else:
                    out.append(i)
                # print(type(i))
            
            return out

            
        output = [
            dict(zip(columns, test(row)))
            for row in cursor.fetchall()
        ]
        # print("AS")

        return output


    def connect(self):
        dsn_tns = cx_Oracle.makedsn(self.parm["server"], self.parm["port"], service_name=self.parm["database"])
        self.conn = cx_Oracle.connect(user=self.parm["username"], password=self.parm["password"], dsn=dsn_tns)
        if self.logService != None:
            self.logService.write("LOG","INFO","LOW","Oracle Database "+self.parm["username"]+"@"+self.parm["database"]+" is connected.","Oracle Database "+self.parm["username"]+"@"+self.parm["database"]+" is connected.")
    def select(self,sql):

    
        # print(self.conn)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            # columns = [col[0] for col in cursor.description]
            # cursor.rowfactory = lambda *args: dict(zip(columns, args))
            r = Recordset()
            r.data = self.dictfetchall(cursor)
            
            return r
        except OperationalError as ex:
            
            self.connect()
            if self.logService != None:
                self.logService.write("LOG","ERROR","HIGH","Oracle Database is not avilable. try to reconnect","cx_Oracle connection is not avilable for select query. try to reconnect that. sql query is "+sql)
            return None
        except Exception as ex:
            # print(ex)
            self.handler.exception = ex
            return None
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
    
    def makeFilterCondition(self,dbtable,filter,ignoreCase=True):
        w = " and ("
        if(type(filter)==dict):
            filter = [filter]
        # print(filter)
        if len(filter)>0:
            index = 0
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
                        # print(f)
                        vl = fl[f]
                        c = f
                
                cl = dbtable.findColumn(c)
                if ignoreCase:
                    c = "upper("+c+")"
                # print(j)
                # print(cn)
                vl= self.formatColumnValue(cl,vl,ignoreCase)
                if cn == "=":
                    ws = c + " = " + vl 
                elif cn == "<>":
                    ws = c + " <> " + vl 
                elif cn == "<":
                    ws = c + " < " + vl 
                elif cn == ">":
                    ws = c + " > " + vl 
                elif cn == "<=":
                    ws = c + " <= " + vl 
                elif cn == ">=":
                    ws = c + " >= " + vl 
                elif cn == "like":
                    ws = c + " like " + vl 
                elif cn == "not like":
                    ws = c + " not like " + vl 
                elif cn == "in":
                    ws = c + " in (" + vl +")"
                elif cn == "not in":
                    ws = c + " not in (" + vl +")"
                
                if index==0:
                    w = w + " " + ws
                else:
                    w = w + " "+ j + " " + ws

                index = index + 1
        # else:

        w = w + ")"
        if w == " and ()":
            w = ""
        return w

    def formatColumnValue(self,column,value,ignoreCase=True):
        cl = column
        v = value
        # print(cl)
        if type(v)!=str and type(v)!=list:
            v = str(v)
        
        if type(v)==str:
            if cl.type == "CHAR":
                if ignoreCase:
                    fv = "upper('"+ v +"')" 
                else:
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
        elif type(v)==list:
            ov = ""
            for v1 in v:
                if cl.type == "CHAR":
                    if ignoreCase:
                        ov = ov+"upper('"+ v1 +"')" 
                    else:
                        ov = ov+"'"+ v1 +"'" 
                    
                elif cl.type == "NUMBER":
                    ov = ov+str(v1)
                elif cl.type == "FUNCTION":
                    ov = ov+str(v1)
                elif cl.type == "DATE":
                    if cl.valueFormat == "":
                        ov = ov+"to_date('"+ v1 +"')" 
                    else:
                        ov = ov+"to_date('"+ v1 +"','"+cl.valueFormat+"')" 
                ov = ov + ","
            fv = ov.strip(",")

        return fv

    def makeSelectSql(self,dbtable,column,filter,order,ignoreCase=True):
        columns = dbtable.columns
        data = dbtable.data
        
        w = self.makeFilterCondition(dbtable,filter,ignoreCase)
        f = ",".join(column)
        o = ",".join(order)
        sql = "select " + f + " from " + dbtable.name+ " where 1 = 1 " + w + " order by " + o
        return sql

    def makeUpdateSql(self,dbtable,filter,autoUpdate=False,autoCommit=False,ignoreCase=False):
        columns = dbtable.columns
        data = dbtable.data
        
        w = self.makeFilterCondition(dbtable,filter,ignoreCase)

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