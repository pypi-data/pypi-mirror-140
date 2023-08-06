import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
class MailSendingEngin:

    def __init__(self):
        self.error = None
        self.message = ""

    def send(self,receiver_email,subject,content,sender=None):
        if sender==None:
            sender=self.username
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = receiver_email   

        part2 = MIMEText(content, "html")
        message.attach(part2)
        return self._send(receiver_email=receiver_email,message=message.as_string(),sender=sender)

    def _send(self,receiver_email,message,sender):
        try:
            if self.connection!=None:
                self.connection.sendmail(sender, receiver_email, message)         
                # print("Successfully sent email")
                return True
            else:
                # print("Server is not connected")
                self.message = 'Server is not connected'
                return False
        except Exception as ex:
            traceback.print_exc()    
            self.error = ex
            self.message = 'unable to send email. '+str(ex)
            # print("Error: unable to send email")
            return False

    def close(self):
        if self.connection!=None:
            self.connection.quit()

class SMTP_TLSConnection(MailSendingEngin):
    def __init__(self,server,port,username,password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def connect(self):
        self.context = ssl.create_default_context()
        try:
            server = smtplib.SMTP(self.server,self.port)
            server.ehlo() # Can be omitted
            server.starttls(context=self.context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(self.username, self.password)
        except Exception as e:
            self.connection = None
            self.error = e
            print(e)
            pass
        finally:
            self.connection = server



class SMTP_SSLConnection(MailSendingEngin):
    def __init__(self,server,port,username,password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def connect(self):
        self.context = ssl.create_default_context()
        try:
            server = smtplib.SMTP_SSL(self.server,self.port)
            server.login(self.username, self.password)
        except Exception as e:
            self.connection = None
            self.error = e
            print(e)
            pass
        finally:
            self.connection = server



class SMTP_Connection(MailSendingEngin):
    def __init__(self,server,port,username,password):
        
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def connect(self):

        try:
            server = smtplib.SMTP(self.server,self.port)
            server.login(self.username, self.password)
        except Exception as e:
            self.connection = None
            self.error = e
            pass
        finally:
            self.connection = server
        
    