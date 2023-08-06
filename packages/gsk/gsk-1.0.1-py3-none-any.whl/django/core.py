from django.db import models
from awgp.django.database import DB
from awgp.common.data import Recordset



class ModelManager(models.Manager):
    def toRecordset(self,map,data=None):
        r = Recordset()
        output = []
        if data == None:
            data = self.all()
        for row in data:
            o = {}
            for m in map:
                o[m.upper()] = row.__dict__[map[m]]
            output.append(o)
        r.data = output
        return r

    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email must be set!')
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        #print(email_)
        return self.get(username=username)

    def getAll(self,map,userId,verbose=None):
        tableName = self.model._meta.db_table
        tableName = tableName.lower()
        dbName = "default"
        if hasattr(self.model, 'use_db'):
            dbName =self.model.use_db
        db = DB(dbName)

        f = ""
        for m in map:
            f = f + "a."+map[m] + " as " + m + ","
        f = f.strip(",")

        sql = "select count(*) as total from v$users_user_model where model_name = '"+tableName+"' and user_Id = '"+str(userId)+"'"
        #print(sql)
        r = db.runSelect(sql)
        if r.get("total") == 0:
            sql = "select "+f+" from "+tableName+" a"
        else:
            sql = "select "+f+" from "+tableName+" a,v$users_user_model b where b.user_id = '"+str(userId)+"' and a.id = b.model_value"
        if verbose != None:
            #print(sql)
            pass
        return db.runSelect(sql)

