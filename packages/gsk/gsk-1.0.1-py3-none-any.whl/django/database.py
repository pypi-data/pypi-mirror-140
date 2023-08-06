import cx_Oracle
from django.db import connections
from django.db import connection
from collections import namedtuple
from awgp.common.data import Recordset
from awgp.database.connection import Connection
class DB:
    def __init__(self,database="default"):
        self.dbName = database
        self.conn = connections
        # cn = self.conn[self.dbName]
        # self.connection = cn.get_new_connection(cn.get_connection_params())
        self.upperCase = True
    def getType(self):
        # print(self.conn[self.dbName]    )
        return self.conn[self.dbName].vendor
        
    def getConnection(self):
        return self.conn[self.dbName]
    
    def runSelect(self,sql,parm=[],new=False):
        
        
        cn = self.conn[self.dbName]
        if new == True:
            if self.conn[self.dbName].connection != None:
                cn = cn.get_new_connection(cn.get_connection_params())
        # print(cn.cursor())
        r = Recordset()
        with cn.cursor() as cursor:
            if len(parm) >  0 :
                cursor.execute(sql,parm)
            else:
                cursor.execute(sql)   
            
            
            r.data = self.dictfetchall(cursor)
            # if new ==True:
            #     cursor.close()
        
        if new == True:
            cn.close()

        return r

        # with self.conn[self.dbName].cursor() as cursor:
        #     # execute the SQL statement
        #     cursor.execute(sql)
        #     # fetch all rows
        #     rows = cursor.fetchall()
        #     if rows:
        #         for row in rows:
        #             print(row)

        #     r = Recordset()
        # #     r.data = self.dictfetchall(cursor)
        #     return r
  
    def runDml(self,sql,parm=None):
        with self.conn[self.dbName].cursor() as cursor:
            if parm==None:
                cursor.execute(sql)
            else:
                # print(parm)
                cursor.execute(sql,parm)
            return cursor

    def dictfetchall(self,cursor):
        "Return all rows from a cursor as a dict"
        # print(self.upperCase)
        if self.upperCase:
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
            # print(row)
            return out
        cursor.arraysize = 200
        output = [
            dict(zip(columns, test(row)))
            for row in cursor.fetchall()
        ]
        # print(cursor.rowcount)
        # print(output)
        return output


    def namedtuplefetchall(self,cursor):
        "Return all rows from a cursor as a namedtuple"
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]


    def toConnection(self):
        parm = {"driver":self.getType()}
        c = Connection(parm)
        c.handler.conn = self.conn[self.dbName]
        return c

#DB.runSelect = staticmethod(DB.runSelect)
