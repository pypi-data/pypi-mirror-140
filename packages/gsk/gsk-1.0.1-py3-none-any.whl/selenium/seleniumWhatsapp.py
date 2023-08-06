import os   
import pyperclip
import time
from awgp.selenium.seleniumLib import *
from awgp.common.json import JSON
from selenium.webdriver.common.keys import Keys
import urllib.parse
class SeleniumWhatsappPost:
    def __init__(self,facebook,cssClassName):
        self.facebook = facebook
        self.cssClassName = cssClassName
        self.document = self.facebook.document
        p = self.document.getElementsByClass(self.cssClassName["POST"])
        # post = p[1]
        self.post = p[1]
        # self.post.click()
        # time.sleep(1)

        # script = '''var d = document.querySelector(".notranslate._5rpu"); 
        # d.focus();
        # '''
        # self.document.runScript(script)

    def addText(self,text):
        # post = self.openPostWindow()
        # p = self.document.getElementsByClass("._3FRCZ.copyable-text.selectable-text")
        # post = p[1]
        pyperclip.copy(text)
        # os.environ['CLIPBOARD'] = text
        
        # pyperclip.paste()
        # self.post.send_keys(Keys.CONTROL, 'v')
        # self.post.send_keys(" ")
        self.post.send_keys((Keys.SHIFT, Keys.INSERT))
        # self.post.key_down(Keys.META)
        # self.post.send_keys('v')
        # self.post.key_up(Keys.META)
    
    def photoSubmit(self):

        cc = self.document.getElementByClass(self.cssClassName["CAPTIONWAPER"])
        c = cc.find_elements_by_css_selector("*")
        # print(c)
        caption = c[1]
        
        # if captionText!= "" and captionText != None:
        #     caption.send_keys(captionText)
        # self.post = caption
        # caption.click()
        caption.send_keys("\n")
        # file = self.document.getElementByClass("._n._5f0v")
        
        time.sleep(.2)

    def findFileInput(self):
        a = self.document.getElementsByClass(self.cssClassName["FILEWAPER"])
        l = a[1].find_elements_by_css_selector(self.cssClassName["FILEBTN"])
        attacheBtn = l[1]
        attacheBtn.click()
        time.sleep(1)
        fileBtn = self.document.getElementByClass("._1dxx-")
        file = fileBtn.find_element_by_tag_name("input")
        return file

    def addPhoto(self,fileList):
        # script = '''var a = document.querySelector(".._3All_._3NrAe");
        # var v = a.querySelectorAll(".rAUz7");

        # '''

        file = self.findFileInput()
        filename = ""
        for f in fileList:
            # time.sleep(.5)
            if f != "" and f != None:
                # filename = filename+'"'+f+'"'
                ff = urllib.parse.unquote(f)
                ff = ff.replace("+"," ")
                try:
                    # print(ff)
                    # pass
                    file.send_keys(ff)
                    # time.sleep(.2)
                except:
                    print("File name error")
                    pass

        
        
        time.sleep(.5)
        self.photoSubmit()

    def submit(self):
        # p = self.document.getElementsByClass("._3FRCZ.copyable-text.selectable-text")
        # post = p[1]
        self.post.send_keys("\n")
        


class SeleniumWhatsapp:
    def __init__(self,browser,cssClassName):
        self.browser = browser        
        self.cssClassName = cssClassName
        self.openPage("https://web.whatsapp.com/")
        


    def login(self,username,password):
        if os.path.exists("whatsapp.cookie"):
            file = open("whatsapp.cookie","rb")
            data = file.read()
            json = JSON.fromString(data)
            # print(json)
            for j in json:
                o = {
                    "name":j["name"],
                    "value":j["value"],
                    "domain":j["domain"],
                    "path":j["path"]
                }
                self.browser.driver.add_cookie(o)
            self.openPage("https://web.whatsapp.com/")
            time.sleep(3)
            # self.browser.driver.get_cookies()
        else:
            
            time.sleep(15)
            # self.document.runScript('alert("Cookie write");')
            # print(self.browser.driver.get_cookies())
            file = open("whatsapp.cookie","w+")
            file.write(JSON.dumps(self.browser.driver.get_cookies()))

    def openPage(self,url):
        self.browser.navigate(url)
        time.sleep(3)
        self.document = self.browser.getDocument()

    def newPost(self):
        post = SeleniumWhatsappPost(self,self.cssClassName)
        return post


    def searchMember(self,name):
        script = '''
        var v = document.querySelector("._3FRCZ.copyable-text.selectable-text");
        v.innerHTML="";
        '''
        self.document.runScript(script)
        search = self.document.getElementByClass(self.cssClassName["SEARCHBOX"])
        # search.innerHTML=""
        search.send_keys(name)
        time.sleep(1)
        search.send_keys("\n")

        
        # return post
    def isLogin(self):
        try:
            login = self.document.getElementByClass(self.cssClassName["CHECKLOGIN"])
        # login = self.document.runScript('if(document.querySelector("._11ozL")==null){return true;}else{return false;}')
        
        # return login
            if login == None:
                return True
            else:
                return False
        except:
            return True
        