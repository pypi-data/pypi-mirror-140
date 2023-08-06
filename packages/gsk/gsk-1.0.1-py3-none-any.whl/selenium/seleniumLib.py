import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeBrowserHtml:
    def __init__(self,driver):
        self.driver = driver

    def runScript(self,script):
        self.driver.execute_script(script)

    def getElementById(self,id):
        return self.driver.find_element_by_id(id)

    def getElementByName(self,name):
        return self.driver.find_element_by_name(name)
    
    def getElementsByName(self,name):
        return self.driver.find_elements_by_name(name)

    def getElementByClass(self,name):
        return self.driver.find_element_by_css_selector(name)

    def getElementsByClass(self,name):
        return self.driver.find_elements_by_css_selector(name)

    def getElementByTagName(self,name):
        return self.driver.find_element_by_tag_name(name)

    def getElementsByTagName(self,name):
        return self.driver.find_elements_by_tag_name(name)
    

class ChromeBrowser:

    def __init__(self,driverPath):
        option = Options()
        option.add_argument("--disable-infobars")
        option.add_argument("start-maximized")
        option.add_argument("--disable-extensions")
        option.add_experimental_option("prefs", { 
            "profile.default_content_setting_values.notifications": 1 
        })
        self.driver = webdriver.Chrome(chrome_options=option,executable_path=driverPath)

    def navigate(self,path):
        self.driver.get(path)


    def getDocument(self):
        return ChromeBrowserHtml(self.driver)

    def quit(self):
        self.driver.quit()