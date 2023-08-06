import os   

import time
from awgp.selenium.seleniumLib import *
from awgp.common.json import JSON
class SeleniumFacebookPost:
    def __init__(self,facebook):
        self.facebook = facebook
        self.document = self.facebook.document
        self.post = self.document.getElementByClass(".notranslate._5rpu")
        self.post.click()
        time.sleep(1)

        script = '''var d = document.querySelector(".notranslate._5rpu"); 
        d.focus();
        '''
        self.document.runScript(script)

    def addText(self,text):
        # post = self.openPostWindow()
        self.post.send_keys(text)
        time.sleep(1)

    def addPhoto(self,filename):
        file = self.document.getElementByClass("._n._5f0v")
        file.send_keys(filename)
        time.sleep(5)

    def submit(self):
        script = '''
        setTimeout(function()
        {
            console.info("running script")
            var v = document.querySelector("._1mf7._4jy0._4jy3._4jy1._51sy.selected._42ft");
            v.click();
        },2000)
        
        '''
        self.document.runScript(script)
        


class SeleniumFacebook:
    def __init__(self,browser):
        self.browser = browser        
        self.openPage("https://www.facebook.com")
        


    def login(self,username,password):
        if os.path.exists("facebook.cookie"):
            file = open("facebook.cookie","rb")
            data = file.read()
            json = JSON.fromString(data)
            # print(json)
            for j in json:
                o = {
                    "name":j["name"],
                    "value":j["value"],
                    "domain":j["domain"]
                }
                self.browser.driver.add_cookie(o)
            self.openPage("https://www.facebook.com")
            time.sleep(3)
            # self.browser.driver.get_cookies()
        else:
            email = self.document.getElementByName('email')
            pwd = self.document.getElementByName('pass')
            email.send_keys(username)
            pwd.send_keys(password)
            pwd.submit()
            time.sleep(3)
            # print(self.browser.driver.get_cookies())
            file = open("facebook.cookie","w+")
            file.write(JSON.dumps(self.browser.driver.get_cookies()))

    def openPage(self,url):
        self.browser.navigate(url)
        time.sleep(3)
        self.document = self.browser.getDocument()

    def newPost(self):
        post = SeleniumFacebookPost(self)
        return post

    