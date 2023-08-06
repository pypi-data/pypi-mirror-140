
import firebase_admin
from firebase_admin import credentials
import firebase_admin.messaging as messaging

class FirebaseMessage:
    def __init__(self,multiple=True):
        if(multiple==True):
            self.isMultiple = multiple
            self.message = messaging.MulticastMessage(tokens=[])
        else:
            self.isMultiple = multiple
            self.message = messaging.Message(token="")
            

    def notification(self,title,text):
        self.message.notification = messaging.Notification(title=title,body=text)

    def setExtra(self,data):
        
        self.message.data = data

    def setTokens(self,tokens):
        if self.isMultiple==True:
            self.message.tokens = tokens
        else:
            self.message.token = tokens

class FirebaseMessging:
    def __init__(self,certificateFile):
        self.cred = credentials.Certificate(certificateFile)
        self.default_app = firebase_admin.initialize_app(self.cred)

    def sendTo(self,message,tokens):
        print(tokens)
        message.setTokens(tokens)
        if message.isMultiple==True:
            response = messaging.send_multicast(message.message)
        else:
            response = messaging.send(message.message)
        return response