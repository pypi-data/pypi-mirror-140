import imaplib
import base64
import os
import email
from flufl.bounce import scan_message

class MailMessage:

    def __init__(self,message_type,data,id,mailbox):
        self.type = message_type
        self.mailbox = mailbox
        self.id = id
        self.obj = data
        self.raw = self.obj[0][1]
        # print(type(raw)))
        if(str(type(self.raw))=="string"):
            # print("a")
            raw_email_string = self.raw.decode('utf-8')
            self.data = email.message_from_string(raw_email_string)
        elif(str(type(self.raw))=="<class 'bytes'>"):
            raw_email_string = self.raw.decode('utf-8')
            # print("b")
            self.data = email.message_from_string(raw_email_string)

    def downloadAttachement(self,svdir):
        if self.data.get_content_maintype() != 'multipart':
            print(self.data.get_content_maintype())
            return

        for part in self.data.walk():
            if part.get_content_maintype() == 'multipart':
                # print("B")
                continue
            if part.get('Content-Disposition') is None:
                # print("C")
                continue
            filename=part.get_filename()
            if filename is not None:
                sv_path = os.path.join(svdir, filename)
                if not os.path.isfile(sv_path):
                
                    fp = open(sv_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    return sv_path
                else:
                    print("File is already exist")
        return ""
    
    def getOrignalReceiptent(self):
        recipients = scan_message(self.data)
        # print(self.id)
        if len(recipients) > 0:
            receptnet = str(recipients.pop(),"utf-8")
            # print(receptnet)
            return receptnet
        return None

    def flagAsRead(self):
        self.mailbox.imap.store(self.id, '+FLAGS', '\Seen')



class MailBox:
    def __init__(self):
        pass

    def login(self,host,username,password):
        self.imap = imaplib.IMAP4_SSL(host)
        self.imap.login(username,password)

    def select(self,mailbox="Inbox",readonly=True):
        self.imap.select(mailbox,readonly)

    def search(self,key):
        # type, data = self.mail.search(None, 'FROM','"Mail Delivery Subsystem <mailer-daemon@googlemail.com>"')
        type, data = self.imap.search(None, key)
        # type,data = self.mail.uid('search', None, 'HEADER Subject "Delivery Status Notification (Failure)"')
        # print(data)
        mail_ids = data[0]
        # print(mail_ids)
        self.id_list = mail_ids.split()
        # print(self.id_list)
        return self.id_list

    def fetch(self,id):
        typ, data = self.imap.fetch(id, '(RFC822)' )
        msg = MailMessage(typ,data,id,self)
        return msg
