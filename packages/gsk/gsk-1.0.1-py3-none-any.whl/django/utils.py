from awgp.django.database import DB
def JsonToModel(model,data):
    for d in data:
        # f = model._meta.get_field(f["id"])
        # model
        if data[d]== "":
            data[d] = None
        model.__dict__[d] = data[d]
    
    return model

def ModelToJson(model):
    output = {}
    for field in model._meta.fields:
        output[field.name] = model.__dict__[field.name]
    return output

    
def GetModelsHierarchyUp(model,field,fid):
    data = []
    def __getParentOfModel(model,field,fid,data):
        #lookup = "%s__contains" % field
        #m = model.objects.get(**{lookup:id})
        m = model.objects.get(id=fid)

        field_object = m._meta.get_field(field)
        field_value = getattr(m, field_object.attname)
        data.append(m)
        if field_value != None:
            data = __getParentOfModel(model,field,field_value,data)
        return data
    data = __getParentOfModel(model,field,fid,data)
    return data



def GetModelsHierarchyDown(model,field,fid):
    data = []
    def __getParentOfModelDown(model,field,fid,data):
        db = DB("default")
        tableName = model._meta.db_table
        sql = "select id from "+tableName+" where "+field+"_id = "+str(fid)
        r = db.runSelect(sql)
        
        for ml in r.range():
            r.moveRecord(ml)
            data.append(r.get('id'))
            data = __getParentOfModelDown(model,field,r.get("id"),data)

        return data
    data.append(fid)
    data = __getParentOfModelDown(model,field,fid,data)
    return data




def ApplyAutomation(m):
    primary_key="id"
    db = DB()
    db.upperCase=False

    # print()
    # print(m._meta.fields)
    for field in m._meta.fields:
        # print(m.__dict__[field])
        if field.primary_key==True:
            primary_key = field.name
    
    modelName = m.__class__.__name__
    
    sql = "select * from core_automation where document = '{model}'".format(model=modelName)
    # print(sql)
    atList = db.runSelect(sql)
    
    
    # print(cnList.data)
    if len(atList.data)>0:
        sql = "select * from core_automation_action where automation_id = '{autoCode}'".format(autoCode=atList.get("code"))
        # print(sql)
        acList = db.runSelect(sql)

        tableNamme = m._meta.db_table
        pv = m.__dict__[primary_key]
        sql = "select count(*) as total from {table} where {field} = '{value}'".format(table=tableNamme,field=primary_key,value=pv)
        r = db.runSelect(sql)
        if r.get("total")==0:

            cnStat = True
            sql = "select * from core_automation_condition where automation_id = '{autoCode}' and transection = 'INSERT'".format(autoCode=atList.get("code"))
            # print(sql)
            cnList = db.runSelect(sql)
            if atList.get("default_accept")==False and len(cnList.data)==0:
                cnStat=False
            for cn in cnList.data:
                # print(cn)
                match = False
                if cn["condition"]=="EQULE":
                    if str(m.__dict__[cn["field_name"]]) == str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="NOTEQULE":
                    if str(m.__dict__[cn["field_name"]]) != str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="LESSTHEN":
                    if str(m.__dict__[cn["field_name"]]) < str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="GRATERTHEN":
                    if str(m.__dict__[cn["field_name"]]) > str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="IN":
                    ar = str(cn["field_value"]).split(",")
                    if str(m.__dict__[cn["field_name"]]) in ar:
                        match=True
                elif cn["condition"]=="NOTIN":
                    ar = str(zcn["field_value"]).split(",")
                    if str(m.__dict__[cn["field_name"]]) not in ar:
                        match=True
                if match!=True:
                    cnStat=False
            if cnStat == True:
                # print(acList.data)
                for ac in acList.data:
                    m.__dict__[ac["field_name"]] = ac["field_value"]
        else:
            cnStat = True
            sql = "select * from core_automation_condition where automation_id = '{autoCode}' and transection = 'UPDATE'".format(autoCode=atList.get("code"))
            cnList = db.runSelect(sql)
            if atList.get("default_accept")==False and len(cnList.data)==0:
                cnStat=False
            for cn in cnList.data:
                match = False
                if cn["condition"]=="EQULE":
                    if str(m.__dict__[cn["field_name"]]) == str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="NOTEQULE":
                    if str(m.__dict__[cn["field_name"]]) != str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="LESSTHEN":
                    if str(m.__dict__[cn["field_name"]]) < str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="GRATERTHEN":
                    if str(m.__dict__[cn["field_name"]]) > str(cn["field_value"]):
                        match=True
                elif cn["condition"]=="IN":
                    ar = str(cn["field_value"]).split(",")
                    if str(m.__dict__[cn["field_name"]]) in ar:
                        match=True
                elif cn["condition"]=="NOTIN":
                    ar = str(zcn["field_value"]).split(",")
                    if str(m.__dict__[cn["field_name"]]) not in ar:
                        match=True
                if match!=True:
                    cnStat=False
            if cnStat == True:
                for ac in acList.data:
                    m.__dict__[ac["field_name"]] = ac["field_value"]
    
    return m