from awgp.django.database import DB
from awgp.common.data import Recordset
from awgp.common import *



from django.db.models.functions import Lower, Substr
from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce,Cast,Greatest
from django.db.models import FloatField,Max,IntegerField



import re
import datetime

def NamingSequance(model,column,pattern,data={}):
    # pattern = pattern.upper()
    if pattern != "" :
        
        match = re.findall(r'\{(.*?)\}',pattern)
        date = datetime.datetime.now()
        for key in match:
            vc = key.split(":")
            if len(vc) > 1 :
                if vc[0] == "F" :
                    fx = vc[1].split("<")
                    if len(fx) > 1 :
                        fn = fx[0]
                        val = globals()[fn](data[fieldName])
                    else :
                        fieldName = fx[0]
                        val = data[fieldName]
                vc = val
            if key == "DD":
                vc = date.day
            if key == "MM":
                vc = date.month
            if key == "YY":
                vc = date.year - 2000
            if key == "YYYY":
                vc = date.year

            pattern = pattern.replace('{'+key+'}',str(vc))
            
        hashLen = 0
       
        pp =""
        
        for i in list(range(len(pattern))):
            if pattern[i]=="#":
                hashLen=hashLen+1
            else:
                pp += pattern[i]

        hashPos = len(pp)
        pattern = pp
        pattern = pattern.upper()
        pattern = re.sub(r'/[^A-Za-z0-9\-\/]/','',pattern)
        #print(column+" LIKE '"+pattern+"%%'")
        o = model.objects.extra(where=[column+" LIKE '"+pattern+"%%'"], params=[])
        # print(column+" LIKE '"+pattern+"%%'")
        out = model.objects.extra(where=[column+" LIKE '"+pattern+"%%'"], params=[]).aggregate(out=Coalesce(Max(Cast(Substr(column,hashPos+1,100),output_field=IntegerField())),0))
        # print(out)
        out = str(out["out"]+1)
        output = pattern+out.zfill(hashLen)
        #print(output)
        return output
