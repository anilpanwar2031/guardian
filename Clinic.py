from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep




class ClinicSwitch:
    
    def __init__(self,
        
        browser,
        pre_flow:dict,
       
        
        post_flow:dict,
        search_button_path:str,
        queries:dict,
        clinic_details:dict,
        search_filters:dict,
         ):
          
        self.pre_flow = pre_flow
        self.browser = browser
       
        
        self.search_button_path = search_button_path
        self.post_flow = post_flow
       
        self.queries =queries

        self.clinic_details= clinic_details
        
        self.search_filters =search_filters
    # perfrom search only it consits 4 parts pre part of search if any  and post part after making query if any and additional inputs like dob with their relative XPATH as key pair value in dictionary
    
    def __str__(self):
        return f" query : {self.query}"
    
   # @log_decorator("search_function")
    def performS(self):

        wait = WebDriverWait(self.browser,10)


        # pre pre_flow before making any queries
        print(self.pre_flow['Clicks'])
     
        if len(self.pre_flow)!=0:
            if len(self.pre_flow['AdditonalInfo']) !=0:                
                if self.pre_flow['AdditonalInfo'].get('sleep'):
                    sleep( self.post_flow['AdditonalInfo'].get('sleep'))
                if self.pre_flow['AdditonalInfo'].get("script"):
                    js=self.pre_flow['AdditonalInfo'].get("script").get("js")
                    arg1=self.pre_flow['AdditonalInfo'].get("script").get("arg1")
                    arg2=self.pre_flow['AdditonalInfo'].get("script").get("arg2")
                    
                    
                    self.browser.execute_script()
                        
                      
            for step in self.pre_flow['Clicks']: 
                                              
                ele=wait.until(EC.element_to_be_clickable((By.XPATH,step)))
                try:
                    ele.click()                      
                except:
                    self.browser.execute_script("arguments[0].click();", ele)    

        if len(self.queries)!=0:
            
            for item in self.queries:
                if item.get('AdditonalInfo'):
                    if item['AdditonalInfo'].get("sleep"):
                        sleep(item['AdditonalInfo'].get("sleep"))              
                q=self.clinic_details[item['Data']]
                path =item['Xpath']     
                ele=wait.until(EC.element_to_be_clickable((By.XPATH,path))) 
                ele.clear()                
                print(q)
                ele.send_keys(q)
            
             

        #making SEarach  here
        if len(self.search_button_path)!=0:
            wait.until(EC.element_to_be_clickable((By.XPATH,self.search_button_path))).click()
        

        # flow if any after query

        if len(self.post_flow)!=0:
            if len(self.post_flow['AdditonalInfo']) !=0:
                if self.post_flow['AdditonalInfo'].get('sleep'):
                    sleep( self.post_flow['AdditonalInfo'].get('sleep'))
            if self.post_flow['AdditonalInfo'].get("script"):                
                js=self.post_flow['AdditonalInfo'].get("script").get("js")
                arg1=self.post_flow['AdditonalInfo'].get("script").get("arg1")
                arg2=self.post_flow['AdditonalInfo'].get("script").get("arg2") 
                self.browser.execute_script(js,arg1,arg2)       
                               
            for step in self.post_flow['Clicks']:
                ele=wait.until(EC.element_to_be_clickable((By.XPATH,step)))
                try:
                    ele.click()
                except:
                    self.browser.execute_script("arguments[0].click();", ele)     
        
        
        
        if len(self.search_filters)!=0:
            print(self.search_filters)
            script=self.search_filters['js']
            args1=self.search_filters['arg1']
            args2=self.clinic_details[self.search_filters['arg2']]
            print(args2)
            if self.search_filters.get('wait'):
                wait.until(EC.element_to_be_clickable((By.XPATH,self.search_filters['wait'])))
            t =self.browser.execute_script(script,args1,args2)
            if self.search_filters.get('afterwait'):
                wait.until(EC.element_to_be_clickable((By.XPATH,self.search_filters['afterwait'])))
            print(t,"--------------------------------------------------------")
            
       
       
# document.evaluate("//*[text()='813.00']/ancestor::tr[2]/td[4]/span, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()
        
    
        

