import imaplib, msal, email
from email.header import decode_header
import datetime
from time import sleep, gmtime, strftime
import re
from lxml import etree

def get_access_token(tenantID, clientID, clientSecret):
    
    authority = 'https://login.microsoftonline.com/' + tenantID
    scope = ['https://outlook.office365.com/.default']
    app = msal.ConfidentialClientApplication(clientID, authority=authority, 
          client_credential = clientSecret)
    access_token = app.acquire_token_for_client(scopes=scope)
    return access_token

def generate_auth_string(user, token):
    auth_string = f"user={user}\x01auth=Bearer {token}\x01\x01"
    return auth_string

def authenticate_imap(tenantID, clientID, clientSecret, username):
    #IMAP AUTHENTICATE
    try:
        imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        imap.debug = 0
        access_token = get_access_token(tenantID, clientID, clientSecret)

        imap.authenticate("XOAUTH2", lambda x:generate_auth_string(username,access_token['access_token']))
        status, messages=imap.select('inbox')
        messages = int(messages[0])        # get number of messages
        statusmessage="IMAP Auth Success"
        return imap, messages, statusmessage
    except:
        return '', '', "IMAP Auth Failed"
def mail_time_check(seconds, messages, imap):
    N=10
    sleep(10)
    templist=[]
    status, messages=imap.select('inbox')
    messages = int(messages[0])        # 
    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                temp=msg['Date']
                print(temp)
                try:temp=temp[5:temp.index("+")-1]
                except: temp=temp[5:temp.index("-")-1]
                difference = datetime.datetime.now()-datetime.datetime.strptime(temp, '%d %b %Y %H:%M:%S')
                print(difference.total_seconds())
                templist.append(difference.total_seconds())
    # templist.sort()
    # print(templist)
                if(difference.total_seconds()<=seconds):
                    return "Received Mails within timeframe"
    return "No Mails within timeframe"
def fetch_otp(imap, messages,OtpXpath,EmailTitle,sleep_time=30):
   
    sleep(sleep_time)
    N=10
    status, messages=imap.select('inbox')
    messages = int(messages[0])    
    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                
                msg = email.message_from_bytes(response[1])
                
    
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                print(From)
             
                if isinstance(From, bytes):
                    From = From.decode(encoding)  
                print(From)                      
                print(subject,"<")
                if msg:
                    # iterate over email parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))                        
                        if content_type == "text/html":
                            body = part.get_payload(decode=True).decode()

                           # open(f"{i}.html","w",encoding="utf-8").write(body) 
                            print(EmailTitle)
                            if(EmailTitle in str(body)):  
                                if "!@"  in OtpXpath:
                                    if OtpXpath.split("!@")[1] == "Regex":
                                       
                                        match = re.findall(OtpXpath.split("!@")[0], body)[0]
                                        print(match)
                                        return match, "OTP successfully fetched"  

                                else:                                        
                                    dom = etree.HTML(body)                              
                                    otp  = otp=dom.xpath(OtpXpath)[0].text.strip()
                                    print(otp,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<otppppp")  
                                    return otp, "OTP successfully fetched"  

    return None ,"Email Not Found"                                  
    imap.close()
    imap.logout()
