import easyimap
from time import sleep
from lxml import etree
from imapaccess import *
import re
#xpath="//*[@id='PasswordControl']


class OtpFetcher:
    def __init__(self,imap_host=None, imap_user=None, imap_pass=None,FromEmail=None,OtpXpath=None,EmailTitle=None,tenantID=None,clientID=None,clientSecret=None,username=None,EncryptionType=None,sleep_time=10):
         
        self.imap_host       = imap_host
        self.imap_user       = imap_user
        self.imap_pass       = imap_pass
        self.FromEmail       = FromEmail
        self.OtpXpath        = OtpXpath
        self.EmailTitle      = EmailTitle
        self.tenantID        = tenantID
        self.clientID        = clientID
        self.clientSecret    = clientSecret
        self.username        = username      
        self.EncryptionType  = EncryptionType
        self.sleep_time      = sleep_time
    
                         
    
    def otp_fetch_with_imap(self):
        tenantID     = self.tenantID        
        clientID     = self.clientID
        clientSecret = self.clientSecret
        username     = self.username
        print(tenantID,clientID,clientSecret,username)       
        imap,messages, statusmessage=authenticate_imap(tenantID, clientID, clientSecret, username)
        print(statusmessage)
        if(statusmessage=="IMAP Auth Success"):
            statusmessage=mail_time_check(120000000000, messages, imap)
            print(statusmessage)
            if("Received Mails within timeframe" in statusmessage):
                OTP, statusmessage=fetch_otp(imap, messages,self.OtpXpath,self.EmailTitle,self.sleep_time)
                print(statusmessage)
                if(statusmessage=="OTP successfully fetched"):
                    return OTP
                else:
                    return statusmessage
            else:
                return statusmessage
        else:
            return statusmessage
    def SimpleImapAccess(self):
        sleep(self.sleep_time)
        imapper = easyimap.connect(self.imap_host, self.imap_user, self.imap_pass)
        emails = imapper.listup(10)
        for i in emails:       
             if i.title==self.EmailTitle:
                 Html=str(i.body.encode("utf-8"))
                 otp=re.findall(self.OtpXpath, Html)[0]
                 return otp
            

# tenantID="e44873dc-54c1-425a-8c70-6bd6ee571de4"
# clientID="aa33b5af-9a5a-4cb3-b120-2b831663f414"
# clientSecret="K.g8Q~W6gjw-xk4IE67XzTeA7X2FIcF2ecoyJcnq"
# username="payorportal@sdbmail.com"
# imap,messages, statusmessage=authenticate_imap(tenantID, clientID, clientSecret, username)
# print(statusmessage)
# if(statusmessage=="IMAP Auth Success"):
#      statusmessage=mail_time_check(1200000000000000, messages, imap)
#      print(statusmessage)
#      if("Received Mails within timeframe" in statusmessage):
#          OTP,statusmessage=fetch_otp(imap, messages,"//span[@class='letter-message']","Guardian Life Security Passcode Delivery",0)         
#          print(OTP,statusmessage)         
#      else:
#          print(statusmessage)
# else:
#     print(statusmessage)

# OtpHandler =  OtpFetcher(
 
#     OtpXpath      =    "//span[@class='letter-message']",
#     EmailTitle    =    "Guardian Life Security Passcode Delivery",
#     tenantID      =    "e44873dc-54c1-425a-8c70-6bd6ee571de4",
#     clientID      =    "aa33b5af-9a5a-4cb3-b120-2b831663f414",
#     clientSecret  =    "K.g8Q~W6gjw-xk4IE67XzTeA7X2FIcF2ecoyJcnq",
#     username      =    "payorportal@sdbmail.com",
#     sleep_time    =    10
    
# )    
# OtpHandler.otp_fetch_with_imap()