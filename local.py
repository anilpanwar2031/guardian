from login import Login
from Search import Search
from Scraper import Scraper
from urllib.parse import urlparse
import json
from Clinic import ClinicSwitch
from blob import create_blob_from_message
import datetime
def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]
def responsemaker(InputParameters,final_data,message_id):    
    date_time = datetime.datetime.now()    
    date=date_time.strftime("%d-%m-%Y")
 
    filename=f"{InputParameters['AppName']}/{InputParameters['PayorName']}/{date}/{message_id}.txt"       
    url =create_blob_from_message(filename, json.dumps(final_data,indent=4), 'text') 
    return url    
   
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
   

 
    ScrapingXpaths =[json.loads(x['XPath'])['Xpaths'] for x in data['Xpaths'] if  x['DataContextName']=='EligibilityLogin'][0][0]

    
    username_xpath       =         ScrapingXpaths['UsernameXpath']   
    password_xpath       =         ScrapingXpaths['PasswordXpath'] 
    login_button_xpath   =         ScrapingXpaths['LoginButtonXpath']
    Otp_input_button_xpath  =      ScrapingXpaths['OtpInputXpath']
    Otp_submit_button_xpath =      ScrapingXpaths['OtpSubmitXpath']
    otp_preSteps           =       ScrapingXpaths['PreSteps']
    
    otp_postSteps          =       ScrapingXpaths['PostSteps']
    otp_xpath              =       ScrapingXpaths['OtpXpath']


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
                                otp_wait=   10
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
                "ErrorMessage": "Login failed",
                "Data": []}
            
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
                "Data": []}
            
    
            return
                                            
                
    PatientData = data['PatientData']

    for patient in PatientData:
        
        queries=json.loads(search_main)['Search']['Queries']
        
        s1=Search(browser,  pre_steps , post_step, search_button_xpath, queries,patient,search_filters)
        
        found=True
    
        s1.performS()        
        ScrapingXpaths_=[x for x in data['Xpaths'] if  x['DataContextName'] not in ['EligibilityLogin','ClinicSwitch'] ] #[x for x in data['ScrapingXpaths'] if x['DataContextName']!='EligibilityLogin']
      
        if found==True:          
            scraper_=Scraper(browser,ScrapingXpaths_,InputParameters,message_id)
       
            scraped_data=scraper_.Scrap()
            
                      
        url_=urlparse(browser.current_url)
        
        homepage=str("https://"+url_[1]+url_[2])
        browser.get(homepage)            
        
    browser.quit()
    return scraped_data


def kickoff(message,message_id):      
    return start(message,message_id)
