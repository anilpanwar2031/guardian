from azure_queue import QueueHandler
from login import Login
from Search import Search
from Scraper import Scraper
from urllib.parse import urlparse
import json
from Clinic import ClinicSwitch
from base64 import b64encode,b64decode
from blob import create_blob_from_message
from downloader import  upload_to_blob
from wrapers import deltadentalins, dnoa,deltadentalins_pp,toolkitPP
import datetime
import os
import requests
if not os.path.exists('download'):  
  os.makedirs('download')
def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]
def responsemaker(InputParameters,final_data,message_id):    
    date_time = datetime.datetime.now()    
    date=date_time.strftime("%d%m%Y%H%M%S")
 
    filename=f"{InputParameters['AppName']}/{InputParameters['PayorName']}/{date}/{message_id}.txt"       
    url =create_blob_from_message(InputParameters,filename, json.dumps(final_data,indent=4), 'text') 
    return url    
def api_post(ScheduleId,InputParameters):
    header = {
        'Content-Type': 'application/json',
        'Origin': 'https://sd-ui.azurewebsites.net',
        'Referer': 'https://sd-ui.azurewebsites.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }

    json_data = {
        'UserName': getdata(InputParameters['AppName']).get("UserName"),
        'Password': getdata(InputParameters['AppName']).get("Password"),
    }

    #response = requests.post('https://sd-identityservice.azurewebsites.net/Login', headers = header, json = json_data)
    #token =response.json().get('token',"")
   # print(token)
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiI5YTFhODQ3YS1mZjY3LTQ5MDctOGZlMC0wZDcyZWU0MjZlN2MiLCJ1bmlxdWVfbmFtZSI6ImV2VXNlcjEiLCJhdXRoX3RpbWUiOiI5LzYvMjAyMiA2OjMwOjM0IEFNIiwianRpIjoiZWRkYjM5NzUtZmVjOC00NDEwLTkzZGMtN2RlMzU3ODBmMWIyIiwiYXVkIjpbIlNpbXBsaWZpRGVudGlzdHJ5LmNvbSIsIlNpbXBsaWZpRGVudGlzdHJ5LmNvbSJdLCJpc3MiOiJCUEtUZWNoLmNvbSIsIklzc3VlZEF0IjoiMTIvNS8yMDIyIDU6Mzg6NDYgQU0iLCJDcmVhdGVkRGF0ZSI6IjkvNi8yMDIyIDY6MzA6MzQgQU0iLCJJc0FjdGl2ZSI6IlRydWUiLCJDbGllbnRJZCI6Ijg4YjgwNTAwLWQ1YTktNGM0MC1hNzUzLTM0ZTQzNjk1YzY5ZSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkNsaWVudFVzZXIiLCJuYmYiOjE2NzAyMTg3MjYsImV4cCI6MTY3MDIyNTkyNn0.IXdHFIqjhCg4AM7sAIVTGhQe-JAK4Uf_3q8oJU2koU0"
    url =getdata(InputParameters['AppName']).get("ApiUrl")
    print("urllllllllllllllllllllllllllllll",url)
    payload = {"RequestData": None, "ScheduleId": ScheduleId, "JobStatus": "Completed",
            "Exception": None}
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Cookie': 'ARRAffinity=22a7daa836b64a8ce56c907737553d08297ff2e76cd06a1f52c29956b9a85c17; ARRAffinitySameSite=22a7daa836b64a8ce56c907737553d08297ff2e76cd06a1f52c29956b9a85c17'
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response)

def start(data,message_id):
    InputParameters =data['InputParameters']    

    website=data['Login']
    url                  =      website['Url']
    username             =      website['LoginId']
    password             =      website['Password']
    OtpRequired          =      website['OtpRequired']
    OtpEmail             =      website['OtpEmail']
    OtpEmailPassword     =      website.get('OtpEmailPassword',"")
    EmailProvierUrl      =      website.get('EmailProvierUrl',"")
    WebsiteId__          =      InputParameters.get("WebsiteId","")

    ScrapingXpaths =[json.loads(x['XPath'])['Xpaths'] for x in data['Xpaths'] if  x['DataContextName']=='EligibilityLogin'][0][0]

    if url.startswith("https://www.providerpayments.com"):
        WebsiteId__ ="ECHOPORTAL_001"
        OtpRequired =True

    username_xpath       =         ScrapingXpaths['UsernameXpath']   
    password_xpath       =         ScrapingXpaths['PasswordXpath'] 
    login_button_xpath   =         ScrapingXpaths['LoginButtonXpath']
    Otp_input_button_xpath  =      ScrapingXpaths['OtpInputXpath']
    Otp_submit_button_xpath =      ScrapingXpaths['OtpSubmitXpath']
    otp_preSteps           =       ScrapingXpaths['PreSteps']
    
    otp_postSteps          =       ScrapingXpaths['PostSteps']
    otp_xpath              =       ScrapingXpaths['OtpXpath']
    LoginAdditionalInfo    =       ScrapingXpaths.get("AdditionalInfo",{})

    search_main=data['SearchParameters'][0]['JsonSettings']
   
    search=json.loads(search_main)['Search']['Settings']
    pre_steps            =      search['PreSteps']
    search_button_xpath  =      search['SearchButtonXpath']
    post_step            =      search['PostSteps']
    search_filters       =      search.get('SearchFilter',{})


    
    login_     =         Login(url  =url,
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
                                otp_wait=   10,
                                website_id=WebsiteId__,
                                additionalInfo=LoginAdditionalInfo
                                
                                )
    browser=None
    try:
        browser    =         login_.performlogin()
    except:
        final = {
                "ClientId": InputParameters['ClientId'],
                "PayorId": InputParameters['PayorId'],
                "AppName": InputParameters['AppName'],  
                "IsError":True,   
                "ErrorMessage" :"Invalid Credentials to Payor Portal"  ,                   
                "Message": "Extraction not Completed",
                "Data": None}
            
  
        QueueHandler( InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))   
        return    

     
    if InputParameters.get('ClinicDetails'):
        data_clinic=[json.loads(x['XPath']) for x in data['Xpaths'] if  x['DataContextName']=='ClinicSwitch'][0]
        clinic_main=data_clinic
   
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
            
            url=responsemaker(InputParameters,final,message_id)
            QueueHandler( InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))   
            return
                                            
                
    PatientData = data['PatientData']

    for patient in PatientData:
        
        queries=json.loads(search_main)['Search']['Queries']
        
        s1=Search(browser,  pre_steps , post_step, search_button_xpath, queries,patient,search_filters)
        
        found=True
        try:
            s1.performS()
        except:
            found=False    
        
     
        ScrapingXpaths_=[x for x in data['Xpaths'] if  x['DataContextName'] not in ['EligibilityLogin','ClinicSwitch'] ] #[x for x in data['ScrapingXpaths'] if x['DataContextName']!='EligibilityLogin']
        
        
        for contexts in ScrapingXpaths_:
            Xpaths=json.loads(contexts['XPath'])
            core=Xpaths.get("forCore")
            print(core)
            if core==False:
                ScrapingXpaths_.remove(contexts)

        if found:          
            scraper_=Scraper(browser,ScrapingXpaths_,InputParameters,message_id)
       
            scraped_data=scraper_.Scrap()            
            if InputParameters.get('WebsiteId')  =="DELTADENTALINS_001" and InputParameters["AppName"]== "Eligibility":
                request =data
                request['PatientData'] =[patient]                                                 
                scraped_data= deltadentalins.main(scraped_data,request)

            elif InputParameters.get('WebsiteId')=="DNOACONNECT_001" and InputParameters["AppName"]== "Eligibility":
                scraped_data= dnoa.main(scraped_data)

            elif InputParameters["AppName"]== "Payment Processing":            
                from wrapers import toolkitPP
                if InputParameters['PayorName'] =="Delta Dental Ins":
                    scraped_data= toolkitPP.main(scraped_data)

                if InputParameters['PayorName'] =="Delta Dental Toolkit":
                    scraped_data=toolkitPP.main(scraped_data)                    
                if InputParameters['PayorName'] =="Delta Dental.Com":
                    scraped_data=toolkitPP.main(scraped_data)     
                if InputParameters['PayorName'] =="Cigna":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Blue Cross Blue Shield":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Dental Network of America":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Post Employment Health Plan":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Metlife":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Select Health":
                    scraped_data=toolkitPP.main(scraped_data) 
                if InputParameters['PayorName'] =="PayPlus":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Humana":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] =="Anthem":
                    scraped_data=toolkitPP.main(scraped_data)  
                if InputParameters['PayorName'] =="Government Employees Health Association-GEHA":
                    scraped_data=toolkitPP.main(scraped_data) 
                if InputParameters['PayorName'].startswith("Regence BCBS"):
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] in "United Healthcare":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] in "Availity":
                    scraped_data=toolkitPP.main(scraped_data)                                                                              
                if InputParameters['PayorName'] in "United Medical Resources":
                    scraped_data=toolkitPP.main(scraped_data)
                if InputParameters['PayorName'] in "Deseret Mutual Benefit Administrators":
                    scraped_data=toolkitPP.main(scraped_data)                                                                              
                if InputParameters['PayorName'] in "EMI Health":
                    scraped_data=toolkitPP.main(scraped_data)  
                if InputParameters['PayorName'] in "HNB-Echo":                    
                    scraped_data=toolkitPP.main(scraped_data)       
                if InputParameters['PayorName'] in ["Delta Dental Illinois", "Delta Dental Connecticut", "Delta Dental of New Jersey", "Delta Dental of Washington", "Delta Dental of Colorado", "Delta Dental Iowa", "Delta Dental of Massachusetts", "Delta Dental of Idaho", "Delta Dental North Dakota", "Delta Dental of Oklahoma", "Delta Dental of Rhode Island", "Delta Dental Wyoming", "Delta Dental Alaska", "Delta Dental of Oregon", "Delta Dental Hawaii", "Delta Dental Maine", "Delta Dental NewHampshire", "Delta Dental of Missouri", 'Delta Dental of Arizona', 'Delta Dental Kansas', 'Delta Dental New York', 'Delta Dental Pennsylvania', 'Delta Dental of Virgina', 'Delta dental of ohio', 'Delta Dental of Arizona', "Regence Traditional", 'Ameritas', 'Principal', 'Dentist Direct', 'Delta Dental of Arkansas', 'Delta Dental of California', 'Delta Dental of Minnesota', 'Delta Dental of Wisconsin', 'Reliance Standard Life Ins Co', 'Samera Health', 'Lincoln National', 'Direct Care Administrators', 'Standard Insurance Company', 'Merchants Benefit Administration, Inc.']:
                    scraped_data=toolkitPP.main(scraped_data)                                              
                if InputParameters['PayorName'] in "United Concordia":
                    from wrapers import echo
                    scraped_data=echo.main(scraped_data)                                                        
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
                        if patient.get("PPTransPayorListID"):
                            ctxt['PPTransPayorListID']=patient.get("PPTransPayorListID")    
                                                                            
            
                    else:
                        for dct in ctxt:
                                                       
                            dct['ClientId']=InputParameters.get('ClientId')
                            dct['EligibilityVerificationId']=patient.get('EligibilityVerificationId')
                            if patient.get('PatientId'):
                                dct['PatientId']=patient.get('PatientId')
                            if patient.get("RcmGridViewId"):                
                                dct['RcmGridViewId']=patient.get("RcmGridViewId")
                            if patient.get("PPGridViewId"):
                                ctxt['PPGridViewId']=patient.get("PPGridViewId")                                
                            if patient.get("PPTransPayorListID"):
                                ctxt['PPTransPayorListID']=patient.get("PPTransPayorListID")                                    
                data_=[]                
                if type(scraped_data[i]).__name__=="dict":
                    data_= [scraped_data[i]]
                else:
                    data_=scraped_data[i]
                   
          
            for i, obj in enumerate(scraped_data['PpEobClaimDetail'], start=1):
                obj["RecordID"] = i
            for i, obj in enumerate(scraped_data['EFTPatients'], start=1):
                obj["RecordID"] = i
            for i, obj in enumerate(scraped_data['PpEobClaimMaster'], start=1):
                obj["RecordID"] = i                               
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
                "EligibilityVerificationId": patient['EligibilityVerificationId'],
                "ClinicServerId": patient['ClinicServerId'],
                'ETFNumber': patient.get('number'),
                "ErrorMessage": "EFT not found",
                "IsError":True,
                "Message": "Extraction not Completed",
                "Data":None
                }
            
            
             
            QueueHandler(InputParameters['AppName']).send_message(b64encode(bytes(json.dumps(final,indent=4), 'utf-8')).decode('utf-8'))   
                                        
        url_=urlparse(browser.current_url)
        
        homepage=str("https://"+url_[1]+url_[2])
        browser.get(homepage)            
        
    browser.quit()


def kickoff(message,message_id):  
    
    start(message,message_id)


