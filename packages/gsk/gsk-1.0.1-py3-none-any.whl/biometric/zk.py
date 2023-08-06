from zk import ZK, const
import json
from zk import ZK, const
from zk.user import User
from zk.finger import Finger
from zk.attendance import Attendance
from zk.exception import ZKErrorResponse, ZKNetworkError
class ZKLib:
    def __init__(self,ip,port,timeout):
        self.conn = None
        zk = ZK(ip, port=int(port), timeout=timeout)
        self.connected = False
        if zk.helper.test_ping():

            self.conn = zk.connect()
            self.connected = True
        else:
            self.conn = None

    def lock(self):
        if self.conn!=None:
            self.conn.disable_device()

    def unlock(self):
        if self.conn!=None:
            self.conn.enable_device()

    def erase_device(self):
        if self.conn!=None:
            self.conn.disable_device()
            self.conn.clear_data()
            self.conn.clear_attendance()
            self.conn.read_sizes()

    
    def getAttendance(self,clear=False):
        if self.conn!=None:
            x = self.conn.disable_device()
            attendances = self.conn.get_attendance()
            if clear==True:
                self.conn.clear_attendance()
            x = self.conn.enable_device()
            return attendances
        return []

    def clearAttendance(self):
        if self.conn!=None:
            
            x = self.conn.disable_device()
            xx = self.conn.clear_attendance()
            x = self.conn.enable_device()
            return xx
        return None

    def getUsers(self):
        if self.conn!=None:
            x = self.conn.disable_device()
            users = self.conn.get_users()
            x = self.conn.enable_device()
            return users
        return []

    def importBackup(self,filename):
        if self.conn!=None:
            
            infile = open(filename, 'r')
            data = json.load(infile)
            infile.close()
            # self.erase_device() 
            self.format()
            self.conn.disable_device()
            users = [User.json_unpack(u) for u in data['users']]
            templates = [Finger.json_unpack(t) for t in data['templates']]
            for u in users:
                temps = list(filter(lambda f: f.uid ==u.uid, templates))
                self.conn.save_user_template(u,temps)
            self.conn.enable_device()
            self.conn.read_sizes()

    def getTemplate(self,fpid):
        if self.conn!=None:
                
            templates = self.conn.get_templates()
            out = [t.json_pack() for t in templates]
            o = []
            for t in out:
                # print(str(t["uid"])+"..."+str(fpid))
                # print(fpid)
                if str(t['uid']) == str(fpid):
                    # print(t)
                    o.append(t)
            return o
        return []
    def exportBackup(self):

        if self.conn!=None:
            templates = self.conn.get_templates()
            
            serialnumber = self.conn.get_serialnumber()
            fp_version = self.conn.get_fp_version()
            users = self.conn.get_users()
            # inicio = time.time()

            output = open("fp_templage.json", 'w')
            data = {
                'version':'1.00jut',
                'serial': serialnumber,
                'fp_version': fp_version,
                'users': [u.__dict__ for u in users],
                'templates':[t.json_pack() for t in templates]
                }
            json.dump(data, output, indent=1)
            output.close()

    def init(self):
        if self.conn!=None:
            
            self.addUser(2,'ENROLLER',const.USER_ENROLLER,'01092021',"2",'')
            self.addUser(1,'ADMIN',const.USER_ADMIN,'94121122',"1",'')

    def format(self):
        if self.conn!=None:
                

            self.conn.clear_attendance()
            user = self.getUsers()
            user = list(map(lambda x: x.__dict__, user))
            
            for u in user:
                # print(u)
                self.deleteUser(u["uid"])
            
        

    def addUser(self,uid,name,privilege,password,user_id,group_id):
        if self.conn!=None:
            
            exist = False
            name = name.upper()
            ul = self.conn.get_users()
            
            # print(uid)
            for u in ul:
                # print(u.uid)
                if u.uid == uid:
                    exist = True
            # x = self.conn.disable_device()
            if exist == False:
                print("User add")
                xr = self.conn.set_user(uid=uid,name=name,privilege=privilege,user_id=user_id,password=password,group_id=group_id)
                return xr
            else:
                print("User exist")
                return None
            # x = self.conn.enable_device()
            # print(xr)
        return None

    def addFingureprint(self,user,template):
        if self.conn!=None:
            
            users = [User.json_unpack(u) for u in user]
            templates = [Finger.json_unpack(t) for t in template]
            for u in users:
                temps = list(filter(lambda f: f.uid ==u.uid, templates))
                self.conn.save_user_template(u,temps)
        

    def deleteUser(self,uid):
        if self.conn!=None:
            rx = self.conn.delete_user(uid=uid)
            return rx

    def testVoice(self):
        if self.conn!=None:
            
            rx = self.conn.test_voice()


    def disconect(self):
        if self.conn!=None:
            
            self.conn.disconnect()