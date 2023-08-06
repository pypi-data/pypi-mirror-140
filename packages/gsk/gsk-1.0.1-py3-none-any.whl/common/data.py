import simplejson as json
from awgp.common.json import JSON
from operator import itemgetter
import datetime 
from django.core import serializers

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

class RecordsetColumn:
    def __init__(self,name):
        self.type = "CHAR"
        self.name = name.upper()
        self.size = 30
        self.defaultValue = ""
        self.valueFormat = ""
        self.constraint = None
        self.autonumber = False
    def __str__(self):
        return self.name

class Recordset:
    def __init__(self):
        self.index = 0
        self.data = []
        self.columns = []
    def addColumn(self,column,value):
        self.columns.append(column)
        for i in self.range():
            self.data[i][column.name]=value
    def findColumn(self,name):
        for col in self.columns:
            # print(col.name)
            # print(name)
            # print("\n")
            if col.name == name.upper():
                return col
        return None

    def enableAutoNumber(self,name):
        c = self.findColumn(name)
        if c != None:
            c.autonumber = True

    def setColumnValueFormat(self,column,format):
        col = self.findColumn(column)
        col.valueFormat = format

    def setColumnType(self,column,columnType,valueFormat=""):
        col = self.findColumn(column)
        col.type = columnType.upper()
        col.valueFormat = valueFormat

    def count(self):
        return len(self.data)
        
    def moveRecord(self,index):
        self.index = index

    def add(self,data):
        out = {}
        if data != None:
            for k in data:
                if data[k] == None:
                    out[k.upper()] = ""
                else:
                    out[k.upper()] = data[k]
                # print(out[k.upper()])
            if len(self.data) == 0:
                for i in out:
                    c = RecordsetColumn(i)
                    self.addColumn(c,c.defaultValue)
            
            
                # data.update(k.upper(),v)
            self.data.append(out)
    
    def addValue(self,data):
        self.add(data)

    def set(self,name,value):
        name = name.upper()
        self.data[self.index][name] = value

    def getColumnAsArray(self,columnName):
        output = []
        for i in self.data:
            output.append(i[columnName])

        
        return output

    def get(self,name):
        # name = name.upper()
        if name in self.data[self.index]:
            return self.data[self.index][name]
        else:
            return None

    def getRow(self):
        return self.data[self.index]

    def setData(self,data):
        self.data = data

    def getJson(self):
        return json.dumps(self.data,default=myconverter)

    def count(self):
        return len(self.data)

    def range(self):
        return list(range(self.count()))

    def order_by(self,field):
        self.data = sorted(self.data, key=itemgetter(field))

    def check(self,column,value):
        for i in self.range():
            self.moveRecord(i)
            if self.get(column)==value:
                return True
        return False

    def _fromQueryset(self,queryset):
        jsonStr = serializers.serialize('json', queryset)
        
        j = JSON.fromString(jsonStr)
        out = []
        for o in j:
            # print(o["fields"])
            o["fields"]["pk"] = o["pk"]
            # ot = []
            for on in o["fields"]:
                if o["fields"][on]==None:
                    o["fields"][on] = ""
            # print(o["fields"])
            out.append(o["fields"])
        self.data = out

    def fromQueryset(self,queryset,map=None):
        
        if map == None:
            return self._fromQueryset(queryset)
        else:
            self.data = []
            for row in queryset:
                o = {}
                for m in map:
                    if(type(map[m])==str):
                        r = row.__dict__[map[m]]
                        f = None
                    elif(type(map[m])==dict):
                        r = row.__dict__[map[m]["name"]]
                        f = map[m]["format"]
                    if str(type(r)) == "<class 'datetime.date'>":
                        r = r.strftime(f)
                    elif str(type(r)) == "<class 'datetime.datetime'>":
                        r = r.strftime(f)
                    if r==None:
                        r=""
                    
                    o[m.upper()] = r
                self.data.append(o)
            
            return
        

class Collection:
    def __init__(self):
        self.data = {}

    def set(self,name,value):
        self.data[name] = value

    def get(self,name):
        return self.data[name]

    def isExist(self,name):
        if name in self.data:
            return True
        else:
            return False
    



class GroupArray():
    def __init__(self):
        self.data = []
        self.key_table = []
        self.value_columns = []
        self.parent_key = None
        self.key = None
    def setValueColulmn(self,columns):
        self.value_columns = columns
    
    
    def setKeyData(self,data,key,parent_id_id=""):
        self.key = key
        self.key_table = data
        self.parent_key = parent_id_id
        
    def setData(self,data,columns=[]):
        self.data = data
        self.value_columns = columns
        
    def findChild(self,code):
        output = []
        for d in self.key_table:
            
            if d[self.parent_key] == code:
                output.append(d)
        return output
    
    def findKeyObject(self,code):
        for d in self.key_table:
            if d["code"] == code:
                return d
        return None
    def addData(self,key):
        for d in self.data:
            if d["account_group_id"] == key["code"]:
                key["child"].append(d)
        return key
                
    def makeHirachicalList(self,code):
        m = self.findChild(code)
        output = []
        for n in m:
            for nc in self.value_columns:
                n[nc]=""
            
            n["childs"] = self.makeHirachicalList(n["code"])
            n = self.addData(n)
            output.append(n)
        return output

    # def addDataWithKey(self,data):
        
    def marge(self):
        d = self.makeHirachicalList(None)
        print(JSON.dumps(d))
        # d = self.addDataWithKey(d)
    
    def findInArray(self,code,data):
        for k in range(len(data)):
            if data[k]["code"] == code:
                return k
        return -1        
    
    def updateGroupData(self,groupCode,row,data,base=False):
        
        
        k = self.findKeyObject(groupCode)
        if k != None:
            kk = self.findInArray(k["code"],data)
            if kk ==-1:
                o = {"code":k["code"],"name":k["name"],"parent_id_id":k["parent_id_id"],"child":[]}
                for i in self.value_columns:
                    # print(k)
                    if row[i]!= None:
                        o[i]=float(row[i])
                    else:
                        o[i] = 0
                if base==True:
                    # print(groupCode,row["account_id"])
                    o["child"].append(row)
                data.append(o)
            else:
                o = data[kk]
                if base == True:
                    # print(groupCode,row["account_id"])
                    o["child"].append(row)
                for i in self.value_columns:
                    if row[i]!= None:
                        o[i]=o[i]+float(row[i])
                        
                    
                data[kk]=o
            data = self.updateGroupData(k["parent_id_id"],row,data)
        return data
                    
    def findChildFromArray(self,code,data):
        output = []
        for d in data:
            
            if d[self.parent_key] == code:
                output.append(d)
        return output
    
    def addDataByArray(self,key,data):
        for d in data:
            if d["parent_id_id"] == key["code"]:
                key["child"].append(d)
        return key
    
    def makeHirachicalListFromArray(self,code,data):
        m = self.findChildFromArray(code,data)
        # print(m)
        output = []
        for n in m:
            
            nc = self.makeHirachicalListFromArray(n["code"],data)
            if "child" in n:
                n["child"] = np.concatenate((n["child"],nc)).tolist()
            else:
                n["child"] = nc
            n = self.addDataByArray(n,data)
            output.append(n)
        return output

    
    def build(self):
        output = []
        for d in self.data:
            output = self.updateGroupData(d["parent_id_id"],d,output,True)
        
        sorted_list = sorted(output, key=lambda x:x["code"])
        for index in range(len(sorted_list)):
            dr = sorted_list[index]["opening_dr"]
            cr = sorted_list[index]["opening_cr"]
            bal = dr-cr
            if bal > 0:
                sorted_list[index]["opening_dr"]=bal
                sorted_list[index]["opening_cr"]=None
            else:
                sorted_list[index]["opening_dr"]=None
                sorted_list[index]["opening_cr"]=0-bal


            dr = sorted_list[index]["closing_dr"]
            cr = sorted_list[index]["closing_cr"]
            bal = dr-cr
            if bal > 0:
                sorted_list[index]["closing_dr"]=bal
                sorted_list[index]["closing_cr"]=None
            else:
                sorted_list[index]["closing_dr"]=None
                sorted_list[index]["closing_cr"]=0-bal
                
        return sorted_list
        # d = self.makeHirachicalListFromArray(None,output)
        # print(JSON.dumps(d))
        
    
class DateFormats:
    
    @staticmethod
    def diff_in_ago(d):
        
        n = datetime.datetime.now()
        dt = n.replace(tzinfo=datetime.timezone.utc) - d.replace(tzinfo=datetime.timezone.utc)
        
        
        out = ""
        if d==n:
            return "Just now"
        
        
        if(dt.days!=0):
            out = str(dt.days)+" ago"
        elif (dt.seconds!=0):
            h = int(dt.seconds/3600)
            if h>0:
                out = str(h)+" hour ago"
            else:
                m = int(dt.seconds/60)
                if m >0:
                    out = str(m)+" minut ago"
                else:
                    out = "Just now"
        
        return out
        