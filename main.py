import sys

sys.path.append('imapsetup')
from WraperHandler import WraperHandler

from azure_queue import QueueHandler
from login import Login
from Search import Search
from Scraper import Scraper
import json
from Clinic import ClinicSwitch
from base64 import b64encode,b64decode
from blob import create_blob_from_message
from downloader import  upload_to_blob
# from wrapers import requesthandler
from azure.storage.blob import BlobServiceClient
import datetime
import os
import random
import string
import requests
from time import sleep

if not os.path.exists('download'):  
  os.makedirs('download')
#s  
def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]
def responsemaker(InputParameters,final_data,message_id):    
    date_time = datetime.datetime.now()    
    date=''.join(random.choices(string.ascii_uppercase +string.digits, k=10))
    filename=f"{InputParameters['AppName']}/{InputParameters['PayorName']}/{date}/{message_id}.txt"       
    url =create_blob_from_message(InputParameters,filename, json.dumps(final_data,indent=4), 'text') 
    return url    
def api_post(ScheduleId,InputParameters):
    
    url =getdata(InputParameters['AppName']).get("ApiUrl")
    print("urllllllllllllllllllllllllllllll",url)
    payload = {"RequestData": None, "ScheduleId": ScheduleId, "JobStatus": "Completed",
            "Exception": None}
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiI5YTFhODQ3YS1mZjY3LTQ5MDctOGZlMC0wZDcyZWU0MjZlN2MiLCJ1bmlxdWVfbmFtZSI6ImV2VXNlcjEiLCJhdXRoX3RpbWUiOiI5LzYvMjAyMiA2OjMwOjM0IEFNIiwianRpIjoiZWRkYjM5NzUtZmVjOC00NDEwLTkzZGMtN2RlMzU3ODBmMWIyIiwiYXVkIjpbIlNpbXBsaWZpRGVudGlzdHJ5LmNvbSIsIlNpbXBsaWZpRGVudGlzdHJ5LmNvbSJdLCJpc3MiOiJCUEtUZWNoLmNvbSIsIklzc3VlZEF0IjoiMTIvNS8yMDIyIDU6Mzg6NDYgQU0iLCJDcmVhdGVkRGF0ZSI6IjkvNi8yMDIyIDY6MzA6MzQgQU0iLCJJc0FjdGl2ZSI6IlRydWUiLCJDbGllbnRJZCI6Ijg4YjgwNTAwLWQ1YTktNGM0MC1hNzUzLTM0ZTQzNjk1YzY5ZSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkNsaWVudFVzZXIiLCJuYmYiOjE2NzAyMTg3MjYsImV4cCI6MTY3MDIyNTkyNn0.IXdHFIqjhCg4AM7sAIVTGhQe-JAK4Uf_3q8oJU2koU0',
        'Content-Type': 'application/json',
        'Cookie': 'ARRAffinity=22a7daa836b64a8ce56c907737553d08297ff2e76cd06a1f52c29956b9a85c17; ARRAffinitySameSite=22a7daa836b64a8ce56c907737553d08297ff2e76cd06a1f52c29956b9a85c17'
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response)

def ErrorPoster(InputParameters,error_message,inputurl):
    
    handler =QueueHandler(InputParameters['AppName'])
    handler.queue_name =getdata(InputParameters['AppName']).get("ErrorQueue")
    error_message["InputURL"] =inputurl
    handler.send_message(b64encode(bytes(json.dumps(error_message,indent=4), 'utf-8')).decode('utf-8'))


def start(data,message_id,inputurl):
    

    data_req                                  =      data
    RequestReceivedFromQueue                  =      None
    loginStartTime                            =      None
    PatientSearchTimeStart                    =      None
    PatientSearchTimeEnd                      =      None
    ScrapingTimeStart                         =      None
    ScrapingTimeEnd                           =      None
    WraperStartTime                           =      None
    WraperEndTime                             =      None
    QueueTimeStart                            =      None
    QueueTimeEnd                              =      None
    RequestReceivedFromQueue                  =      datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    # data                                      =      requesthandler.requestmaker(data)
    InputParameters                           =      data['InputParameters']
    payorname                                 =      InputParameters.get("PayorName")
    os.environ['ConnectionString']            =      getdata(InputParameters["AppName"])["AZURE_STORAGE_CONNECTION_STRING"]
    os.environ['IMAPTableName']               =      getdata(InputParameters["AppName"])["IMAPTableName"]
    website                                   =      data['Login']
    url                                       =      website['Url']
    username                                  =      website['LoginId']
    password                                  =      website['Password']
    OtpRequired                               =      website['OtpRequired']
    print(OtpRequired)
    OtpEmail                                  =      website['OtpEmail']
    OtpEmailPassword                          =      website.get('OtpEmailPassword',"")
    EmailProvierUrl                           =      website.get('EmailProvierUrl',"")
    WebsiteId__                               =      InputParameters.get("WebsiteId","")
    
    ScrapingXpaths                            =      [json.loads(x['XPath'])['Xpaths'] for x in data['Xpaths'] if  x['DataContextName']=='EligibilityLogin'][0][0]
    OtpInstructions                           =      ScrapingXpaths.get('OtpInstructions',{})    
    OtpEmail                                  =      OtpInstructions.get('OtpEmail')
    OtpEmailPassword                          =      OtpInstructions.get('OtpEmailPassword')
    FromEmail                                 =      OtpInstructions.get('FromEmail')
    
    EmailTitle_                               =      OtpInstructions.get('EmailTitle')
    tenantID                                  =      OtpInstructions.get("tenantID")
    clientID                                  =      OtpInstructions.get("clientID")
    clientSecret                              =      OtpInstructions.get("clientSecret")
    ImapSecret                                =      {"tenantID":tenantID,"clientID":clientID,"clientSecret":clientSecret}
    SMTPAddress                               =      OtpInstructions.get("SMTPAddress")
    EncryptionType                            =      OtpInstructions.get("EncryptionType")
    ImapType                                  =      OtpInstructions.get("ImapType")
    otpwait                                   =      OtpInstructions.get("OtpWait")
    
    username_xpath                            =      ScrapingXpaths['UsernameXpath']   
    password_xpath                            =      ScrapingXpaths['PasswordXpath'] 
    login_button_xpath                        =      ScrapingXpaths['LoginButtonXpath']
    Otp_input_button_xpath                    =      ScrapingXpaths['OtpInputXpath']
    Otp_submit_button_xpath                   =      ScrapingXpaths['OtpSubmitXpath']
    otp_preSteps                              =      ScrapingXpaths['PreSteps']
    
    otp_postSteps                             =       ScrapingXpaths['PostSteps']
    otp_xpath                                 =       ScrapingXpaths['OtpXpath']
    LoginAdditionalInfo                       =       ScrapingXpaths.get("AdditionalInfo",{})

    search_main=data['SearchParameters'][0]['JsonSettings']
   
    search=json.loads(search_main)['Search']['Settings']

    pre_steps                                 =      search['PreSteps']
    search_button_xpath                       =      search['SearchButtonXpath']
    post_step                                 =      search['PostSteps']
    search_filters                            =      search.get('SearchFilter',{})
    
    loginStartTime =datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    
    login_                                    =         Login(      
                                                                    url  =url,
                                                                    userid=username,
                                                                    password=password,
                                                                    username_box_xpath= username_xpath,
                                                                    password_box_xpath=password_xpath,
                                                                    login_button_xpath= login_button_xpath,
                                                                    otp_required= OtpRequired,
                                                                    otp_email=  OtpEmail,
                                                                    otp_input_button_xpath= Otp_input_button_xpath,
                                                                    otp_submit_button_xpath= Otp_submit_button_xpath,
                                                                    otpemailpassword=OtpEmailPassword,
                                                                    imaphost= EmailProvierUrl,
                                                                    preSteps=  otp_preSteps,
                                                                    postSteps=  otp_postSteps,
                                                                    otp_xpath= otp_xpath,
                                                                    otp_wait=   otpwait,
                                                                    website_id=WebsiteId__,
                                                                    additionalInfo=LoginAdditionalInfo,
                                                                    EmailTitle =EmailTitle_,
                                                                    ImapSecret=ImapSecret,
                                                                    SMTPAddress=SMTPAddress,
                                                                    EncryptionType=EncryptionType,
                                                                    ImapType=ImapType,
                                                                    FromEmail=FromEmail,
                                                                    payorname=payorname
                                                             )
    browser=None
    try:
        browser    =         login_.performlogin()    
    except:
        for patient in data['PatientData']:
            final =  {
                "ClientId": InputParameters['ClientId'],
                "PayorId": InputParameters['PayorId'],
                "AppName": InputParameters['AppName'],  
                "IsError":True,   
                "ErrorMessage" :"Invalid Credentials to Payor Portal"  ,                   
                "Message": "Extraction not Completed",
                "Data": None}
            QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))
            ErrorPoster(InputParameters,final,inputurl)   
        return    
    
    if(InputParameters.get("PayorName")=="Guardian"):
        sleep(100)
    loginEndTime=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")  
    if InputParameters.get('ClinicDetails'):
        data_clinic=[json.loads(x['XPath']) for x in data['Xpaths'] if  x['DataContextName']=='ClinicSwitch']
        if len(data_clinic)!=0:
            clinic_main=data_clinic[0]    
            clinic=clinic_main['Search']['Settings']
            
            pre_steps_            =      clinic['PreSteps']
            search_button_xpath_  =      clinic['SearchButtonXpath']
            post_step_           =      clinic['PostSteps']
            search_filters_       =      clinic['SearchFilter']    
            queries_=clinic_main['Search']['Queries']      
            s=ClinicSwitch(browser,pre_flow=pre_steps_,post_flow=post_step_,search_button_path=search_button_xpath_,queries=queries_,clinic_details=InputParameters['ClinicDetails'],search_filters=search_filters_)
            try:
                s.performS()
            except:
                final = {
                    "ClientId": InputParameters['ClientId'],
                    "PayorId": InputParameters['PayorId'],
                    "AppName": InputParameters['AppName'],
                    "IsError":True,
                    "ErrorMessage": "Clinic switch failed",
                    "Data": None}
                
          
                QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))   
                return
                                                
                
    PatientData = data['PatientData']
    ScrapingXpaths_=[x for x in data_req['Xpaths'] if  x['DataContextName'] not in ['EligibilityLogin','ClinicSwitch'] ]
    for patient in PatientData:
        PatientSearchTimeStart=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        queries=json.loads(search_main)['Search']['Queries']
        
        s1=Search(browser,  pre_steps , post_step, search_button_xpath, queries,patient,search_filters)
        
        found=True
        try:
            s1.performS()
        except:
            found=False
            PatientSearchTimeEnd=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") 

        PatientSearchTimeEnd=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                      
        for contexts in ScrapingXpaths_:
            Xpaths=json.loads(contexts['XPath'])
            core=Xpaths.get("forCore")
            print(core)
            if core==False:
                ScrapingXpaths_.remove(contexts)

       
        if found:
            ScrapingTimeStart=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")          
            scraper_=Scraper(browser,ScrapingXpaths_,InputParameters,message_id,patient)
            
            scraped_data=scraper_.Scrap()
                        
            for contexts in ScrapingXpaths_:
                datacontext = contexts["DataContextName"]
                Xpaths=json.loads(contexts['XPath'])
                Scraping=Xpaths.get("Scraping")
                if Scraping ==False:
                    del scraped_data[datacontext]

                
            ScrapingTimeEnd=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                     
            WraperStartTime =   datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") 
          
            scraped_data  = WraperHandler(InputParameters,data,scraped_data,patient,browser)
 

                                                
            WraperEndTime =datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")    
            QueueTimeStart =  datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            for i in scraped_data:              
                for ctxt in scraped_data[i]:
                    if type(ctxt).__name__=="dict":
                        ctxt['ClientId']=InputParameters.get('ClientId')
                        ctxt['EligibilityVerificationId']=patient.get('EligibilityVerificationId')
                        if patient.get('PatientId'):
                            ctxt['PatientId']=patient.get('PatientId')
                        if patient.get("RcmGridViewId"):
                            ctxt['RcmGridViewId']=patient.get("RcmGridViewId")
                        if patient.get("PPGridViewId"):
                            ctxt['PPGridViewId']=patient.get("PPGridViewId")             
                        if InputParameters['AppName']==   "Revenue Cycle Management":
                            ctxt["PMSSubscriberId"]=patient.get("SubscriberId")                               
                    else:
                        for dct in ctxt:
                            if InputParameters['AppName']==   "Revenue Cycle Management":
                                ctxt["PMSSubscriberId"]=patient.get("SubscriberId")                                                      
                            dct['ClientId']=InputParameters.get('ClientId')
                            dct['EligibilityVerificationId']=patient.get('EligibilityVerificationId')
                            if patient.get('PatientId'):
                                dct['PatientId']=patient.get('PatientId')
                            if patient.get("RcmGridViewId"):                
                                dct['RcmGridViewId']=patient.get("RcmGridViewId")
                            if patient.get("PPGridViewId"):
                                ctxt['PPGridViewId']=patient.get("PPGridViewId") 
                          
                data_=[]                
                if type(scraped_data[i]).__name__=="dict":                    
                    data_= [scraped_data[i]]
                else:
                    data_=scraped_data[i]
 
            final_data = {
            "ClientId": InputParameters['ClientId'],
        
            "PayorId": InputParameters['PayorId'],
            "AppName": InputParameters['AppName'],
            "EligibilityVerificationId": patient.get('EligibilityVerificationId'),
            "ClinicServerId": patient.get('ClinicServerId'),
            'ETFNumber': patient.get('number'),
            "IsError":False,
            "ErrorMessage":"Completed",
            "Message":"Extraction Completed",
            "Data": responsemaker(InputParameters,scraped_data,message_id)}                        
            
            QueueHandler( InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final_data,indent=4), 'utf-8')).decode('utf-8'))     
                                    
            if InputParameters.get("ScheduleId"):                                                
                ScheduleId=InputParameters.get("ScheduleId")
                if ScheduleId > 0:
                    api_post(ScheduleId,InputParameters)
        

        else:
            final = {
                "ClientId": InputParameters['ClientId'],
                "PayorId": InputParameters['PayorId'],
                "AppName": InputParameters['AppName'],
                "EligibilityVerificationId": patient.get('EligibilityVerificationId'),
                "ClinicServerId": patient['ClinicServerId'],
                'ETFNumber': patient.get('number'),
                "ErrorMessage": "EFT not found",
                "IsError":True,
                "Message": "Extraction not Completed",
                "Data":None
                }

            QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))   
            ErrorPoster(InputParameters,final,inputurl)   
                                            
        QueueTimeEnd=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        Audit = {"RequestReceivedFromQueue": RequestReceivedFromQueue,
                 "loginStartTime": loginStartTime, 
                 "loginEndTime": loginEndTime,
                 "SearchStartTime":PatientSearchTimeStart,
                 "SearchEndTime":PatientSearchTimeEnd,
                 "ScrapingTimeStart":ScrapingTimeStart,
                 "ScrapingTimeEnd":ScrapingTimeEnd,
                 "WrapperStartTime":WraperStartTime,
                 "WrapperEndTime":WraperEndTime,
                 "QueueResponseStartTime":QueueTimeStart,
                 "QueueResponeEndTime":QueueTimeEnd,
                 }
        print(json.dumps(Audit,indent=4))
        
        # final_audit={   "ClientId": InputParameters['ClientId'],
        
        #     "PayorId": InputParameters['PayorId'],
        #     "AppName": InputParameters['AppName'],
        #     "PatientId":PatientData[0].get('PatientId'),
        #     "DataContextName":"TimeLogs",
        #     "MessageId":message_id,
        #     "IsError":False,
        #     "ErrorMessage": "",
        #     "Data": responsemaker(InputParameters,Audit,message_id)}
        # responsemaker(InputParameters,data_,f"{message_id}_{i}")
        # QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final_audit,indent=4), 'utf-8')).decode('utf-8'))
      
    browser.quit()

def kickoff(message,message_id,inputurl):
    try:
        start(message,message_id,inputurl)
    except:
        InputParameters =message['InputParameters']
        for patient in message["PatientData"]:
            final  = {
                        "ClientId": InputParameters['ClientId'],
                        "PayorId": InputParameters['PayorId'],
                        "AppName": InputParameters['AppName'],
                        "EligibilityVerificationId": patient['EligibilityVerificationId'],
                        "ClinicServerId": patient['ClinicServerId'],
                        'PatientId': patient.get('PatientId'),
                        "IsError":True,
                        "Message":"Caller Function Failed",
                        "ErrorMessage": "Extraction Failed",
                        "ScrappingSource" : "SD",
                        "Data":None
                        }
            QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))       
            ErrorPoster(InputParameters,final,inputurl)   
    


if __name__ =="__main__":
    Que  =QueueHandler("Payment Processing")
    Que.queue_name="sd-ppclaims-scrapperincoming-que-dev"
    while True:
        messages =Que.receive_message()    
        for msg in messages:            
            print(msg.id)    
            message =  b64decode(msg.content)
            data=message.decode("utf-8")
            blob_url=""
            try:
                message = json.loads(data)
                if(message.get("BlobUrl")):                   
                    connect_str = "DefaultEndpointsProtocol=https;AccountName=sdppcontainerdevsa;AccountKey=YtCZ1RtrjnZZDL2fhTtL1LIq1vMaXO1DgAjsyrQPJpknW7rTlcN8Pu1E5xaB9+7JjEdE/RbVhbva+ASt5dBvDA==;EndpointSuffix=core.windows.net"
                    container_name = "incoming"
                    blob_url=message.get("BlobUrl")
                    try:
                        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
                        container_client = blob_service_client.get_container_client(container_name)
                        _, blob_name = blob_url.split(container_name)
                        blob_name = blob_name.strip('/')
                        blob_client = container_client.get_blob_client(blob_name)
                        var1 = blob_client.download_blob()
                        message= json.loads(var1.content_as_text())
                    except Exception as err: 
                        message=err
                print(message)
                Que.delete_message(msg)
                kickoff(message,msg.id,blob_url)
            except Exception as e:
                print(e)