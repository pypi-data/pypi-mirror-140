import logging
import ldap
import collections
import ldap.modlist as modlist
import base64, sys
from ldap3 import (
    HASHED_SALTED_SHA, MODIFY_REPLACE
)
from ldap3 import *
from ldap3.utils.hashed import hashed


class LDAPAuth:
    def __init__(self,domain,server):
        d = domain.split(".")
        dn = ""
        for d1 in d:
            dn = dn+"dc="+d1+","
        self.base_dn = dn.strip(",")
        self.domain = domain
        self.server = server

        # ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # ldap.protocol_version = 3
        
        # ldap.set_option(ldap.OPT_REFERRALS, 0)
        # ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        # ldap.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        # ldap.set_option( ldap.OPT_X_TLS_DEMAND, True )
        # ldap.set_option( ldap.OPT_DEBUG_LEVEL, 255 )

        self.conn = ldap.initialize("ldaps://"+self.server+":636")
        self.conn = ldap.initialize("ldap://"+self.server)
        # ldap.set_option(ldap.OPT_REFERRALS,0)
        # ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_NEVER)

        self.conn.protocol_version = 3
        
        self.conn.set_option(ldap.OPT_REFERRALS, 0)
        self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.conn.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        self.conn.set_option(ldap.OPT_X_TLS_DEMAND, True )
        # self.conn.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
        # self.conn.set_option(ldap.OPT_X_TLS_NEWCTX, ldap.OPT_ON)
        
        self.loginStat = False

    def login(self,username,password):
        try:
            cn = username+"@"+self.domain
            # dn = "uid="+username+",cn=Users,"+self.base_dn 
            self.authResult = self.conn.simple_bind_s(cn, password)
            self.loginStat = True
            return True
        except Exception as ex:
            # print(ex)
            return False

    def getUser(self,username):
        
        query = "(&(objectClass=USER)(sAMAccountName={username}))".format(username=username)
        # print(query)
        if self.loginStat==True:
            try:
                result = self.conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, query)
                # print(result)        
                return result[0][1]
            except Exception as ex:
                return False
    
    def getGroup(self,groupname):
        query = '(&(objectClass=GROUP)(cn={group_name}))'.format(group_name=groupname)
        if self.loginStat==True:
            try:
                result = self.conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, query)
                return result[0][1]
            except Exception as ex:
                return False
    
 
    def addGroup(self,groupname,description):
        dn = 'CN='+groupname+",OU=Groups,"+self.base_dn

        attrs = {}
        attrs['objectclass'] = ['top'.encode('utf-8'),'group'.encode('utf-8')]
        attrs['cn'] = groupname.encode('utf-8')
        
        attrs['instanceType'] = '4'.encode('utf-8')
        attrs['description'] = description.encode('utf-8')
        attrs['distinguishedName'] = dn.encode('utf-8')
        
        attrs['name'] = groupname.encode('utf-8')
        
        attrs['sAMAccountName'] = groupname.encode('utf-8')
        
        objectCategory = "CN=Group,CN=Schema,CN=Configuration,"+self.base_dn
        attrs['objectCategory'] = objectCategory.encode('utf-8')
        
        ldif = modlist.addModlist(attrs)
        try:
            self.conn.add_s(dn,ldif)
            return True
        except Exception as ex:
            print(ex)
            return False


    def change_password(self,username,password):
        
        hashed_password = hashed(HASHED_SALTED_SHA, password)
        r = self.getUser(username)
        userdn = str(r["distinguishedName"][0].decode("utf-8") )
        unicode_pass = str('\"' + str(password) + '\"')#.encode('iso-8859-1')
        password_value = unicode_pass.encode('utf-16-le')
        return self.conn.modify_s(
            userdn,
            [
                (ldap.MOD_REPLACE, 'userPassword', password.encode()),
                (ldap.MOD_REPLACE, 'unicodePwd', [password_value])
            ],
        )

    def userAddInGroup(self,username,group_name):
    
        r = self.getUser(username)
        userdn = str(r["distinguishedName"][0].decode("utf-8") )
        r = self.getGroup(group_name)
        group_db = r["distinguishedName"][0].decode("utf-8")
        self.conn.modify_s(
            group_db,
            [
                (ldap.MOD_ADD, 'member', [userdn.encode("utf-8")],)
            ],
        )

    def addUser(self,ou,company_id,password,firstname,second_name,mail,mobileNo,department,group):
        
        unicode_pass = str('\"' + str(password) + '\"')#.encode('iso-8859-1')
        # password_value = unicode_pass.encode('utf-16-le')
        if ou != "":
            ou = ","+ou

        r = self.getGroup(group)
        if second_name != "":
            full_name = firstname + " " + second_name
        else:
            full_name = firstname 
        user_dn = 'CN=' + full_name + ou + ',' + self.base_dn
        user_attrs = {}
        user_attrs['objectClass'] = [b'top', b'person', b'organizationalPerson', b'user']   
        user_attrs['cn'] = full_name.encode('utf-8')
        user_attrs['givenName'] = str(firstname).encode('utf-8')
        if second_name!= "":
            user_attrs['sn'] = str(second_name).encode('utf-8')
        user_attrs['displayName'] = ("%s" % full_name).encode('utf-8')
        user_attrs['userAccountControl'] = '544'.encode('utf-8')
        if mail != None:
            user_attrs['mail'] = mail.encode("utf-8")
        user_attrs['uid'] = company_id.encode('utf-8')
        user_attrs['telephoneNumber'] = mobileNo.encode('utf-8')
        user_attrs['physicalDeliveryOfficeName']=department.encode('utf-8')
        user_attrs['pwdLastSet']="-1".encode('utf-8')
        user_attrs['userPrincipalName'] = str(str(company_id)+"@"+self.domain).encode('utf-8')
        user_attrs['sAMAccountname'] = str(company_id).encode('utf-8')
        # user_attrs['userPassword'] = password.encode('iso-8859-1')
        # user_attrs['unicodePwd'] = [unicode_pass.encode('utf-16-le')]
        
        user_ldif = modlist.addModlist(user_attrs)
        try:
            
            self.conn.add_s(user_dn, user_ldif)
            if group != None:
                self.userAddInGroup(company_id,group)
            return user_dn            
        except Exception as ex:
            print(ex)
            return False

