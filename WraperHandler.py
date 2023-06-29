import uuid


def WraperHandler(InputParameters,data,scraped_data,patient,browser):
    scraped_data =scraped_data
    if InputParameters['AppName'] =='Eligibility':        
        if InputParameters.get('WebsiteId')  =="DELTADENTALINS_001" and InputParameters["AppName"]== "Eligibility":
                    request_ =data
                    request_['PatientData'] =[patient]   
                    from wrapers import deltadentalins                                             
                    scraped_data= deltadentalins.main(scraped_data,request_,browser)  
        elif InputParameters.get('WebsiteId')=="DNOACONNECT_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import dnoa
            scraped_data= dnoa.main(scraped_data)
            
        elif InputParameters.get('WebsiteId')=="DENTALOFFICETOOLKIT001" and InputParameters["AppName"]== "Eligibility":
            request_ =data
            request_['PatientData'] =[patient] 
            from wrapers import dentalofficetoolkit
            scraped_data= dentalofficetoolkit.main(scraped_data,request_) 
        elif InputParameters.get('WebsiteId')=="METLIFE001" and InputParameters["AppName"]== "Eligibility":
            request_ =data
            request_['PatientData'] =[patient]
            from wrapers import  metlife
            scraped_data= metlife.main(scraped_data,request_)
        elif InputParameters.get('WebsiteId')=="UNITEDCONCORDIA_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import UC
            scraped_data= UC.main(scraped_data)
        elif InputParameters.get('WebsiteId') in ["CIGNA_001", "2"] and InputParameters["AppName"]== "Eligibility":
            from wrapers import cigna
            scraped_data= cigna.main(scraped_data)    
        elif InputParameters.get('WebsiteId')=="UNITEDHEALTHCARE_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import UHC
            scraped_data= UHC.main(scraped_data) 
        elif InputParameters.get('WebsiteId')=="GUARDIAN_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import guardian
            scraped_data= guardian.main(scraped_data)
        elif InputParameters.get('WebsiteId')=="GEHA_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import geha
            scraped_data= geha.main(scraped_data)
            
        elif InputParameters.get('WebsiteId')=="AMERITAS_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import ameritas
            request_ =data
            request_['PatientData'] =[patient]  
            scraped_data= ameritas.main(scraped_data,request_)    
        elif InputParameters.get('WebsiteId')=="PRINCIPAL_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import principal
            request_ =data
            request_['PatientData'] =[patient]  
            scraped_data= principal.main(scraped_data,request_)
            
        elif InputParameters.get('WebsiteId')=="ILLINOIS_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import illinois
            request_ =data
            request_['PatientData'] =[patient]
            scraped_data= illinois.main(scraped_data,request_)
        elif InputParameters.get('WebsiteId')=="CONNECTICUT_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import connecticut
            request_ =data
            request_['PatientData'] =[patient]  
            scraped_data= connecticut.main(scraped_data,request_) 
        elif InputParameters.get('WebsiteId')=="NEWJERSEY_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import newjersey
            request_ =data
            request_['PatientData'] =[patient]
            scraped_data= newjersey.main(scraped_data,request_) 
        elif InputParameters.get('WebsiteId')=="WASHINGTON_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import washington
            request_ =data
            request_['PatientData'] =[patient]   
            scraped_data= washington.main(scraped_data,request_) 
        elif InputParameters.get('WebsiteId')=="MASSACHUSETTS_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import massachusetts
            request_ =data
            request_['PatientData'] =[patient]  
            scraped_data= massachusetts.main(scraped_data,request_) 

        elif InputParameters.get('WebsiteId')=="COLORADO_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import coloradowrapper
            request_ =data
            request_['PatientData'] =[patient] 
            scraped_data= coloradowrapper.main(scraped_data,request_) 
        elif InputParameters.get('WebsiteId')=="RHODEISLAND_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import rhodeIsland
            request_ =data
            request_['PatientData'] =[patient] 
            scraped_data= rhodeIsland.main(scraped_data,request_)
            
        elif InputParameters.get('WebsiteId')=="OKLAHOMA_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import okalhama
            request_ =data
            request_['PatientData'] =[patient] 
            scraped_data= okalhama.main(scraped_data,request_)

        elif InputParameters.get('WebsiteId')=="MISSOURI_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import missouriwrapper
            request_ =data
            request_['PatientData'] =[patient] 
            scraped_data= missouriwrapper.main(scraped_data,request_)
            
        elif InputParameters.get('WebsiteId')=="IOWA_001" and InputParameters["AppName"]== "Eligibility":
            from wrapers import iowa
            request_ =data
            request_['PatientData'] =[patient] 
            scraped_data= iowa.main(scraped_data,request_)            



    if  InputParameters['AppName']==   "Revenue Cycle Management":            
        if InputParameters['PayorName'] =="Dental Network of America":

            from wrapers import dnoaRCM
            scraped_data=dnoaRCM.main(scraped_data)
        if InputParameters['PayorName'] =="Delta Dental Toolkit": 
            from wrapers import  toolkitRCM                 
            scraped_data=toolkitRCM.main(scraped_data)     
                                        
        if InputParameters['PayorName'] =="United Concordia":
            from wrapers import ucRCM
            scraped_data=ucRCM.main(scraped_data)
                                                    
        if InputParameters['PayorName'] =="Delta Dental.Com":
            from wrapers import ddRCM
            scraped_data=ddRCM.main(scraped_data)   
            
        if InputParameters['PayorName'] =="Cigna":
            from wrapers import cignaRCM
            scraped_data=cignaRCM.main(scraped_data)

        if InputParameters['PayorName'] =="Delta Dental Ins":
            from wrapers import ddinsRCM
            scraped_data=ddinsRCM.main(scraped_data)

        if InputParameters['PayorName'] == "United Healthcare":
            from wrapers import uhcRCM
            scraped_data=uhcRCM.main(scraped_data,data)
        if InputParameters['PayorName'] == "Guardian":
            from wrapers import guardianRCM
            scraped_data=guardianRCM.main(scraped_data)    
        if InputParameters['PayorName'] == "Ameritas":                    
            from wrapers import ameritasRCM
            scraped_data=ameritasRCM.main(scraped_data)   
        if InputParameters['PayorName'] == "Principal":                    
            from wrapers import principalRCM
            scraped_data=principalRCM.main(scraped_data)
        if InputParameters['PayorName'] == "Delta Dental Illinois":
            from wrapers import lIllinoisRCM
            scraped_data=lIllinoisRCM.main(scraped_data)

        if InputParameters['PayorName'] == "Delta Dental Connecticut":
            from wrapers import DDconnecticutRCM
            scraped_data=DDconnecticutRCM.main(scraped_data)
        if InputParameters['PayorName'] == "Delta Dental of New Jersey":
            from wrapers import DDNewjearsyRCM
            scraped_data=DDNewjearsyRCM.main(scraped_data)
        if InputParameters['PayorName'] == "Delta Dental of Washington":
            from wrapers import DDWashingtonRCM
            scraped_data=DDWashingtonRCM.main(scraped_data)
        if InputParameters['PayorName'] == "Delta Dental of Oklahoma":
            from wrapers import DDOklahamaRCM
            scraped_data=DDOklahamaRCM.main(scraped_data)

        if InputParameters['PayorName'] == "Delta Dental of Colorado":
            from wrapers import DDColoradoRCM
            scraped_data=DDColoradoRCM.main(scraped_data)

        if InputParameters['PayorName'] == "Delta Dental Iowa":
            from wrapers import DDIowaRCM
            scraped_data=DDIowaRCM.main(scraped_data)
        if InputParameters['PayorName'] == "Delta Dental of Massachusetts":
            from wrapers import DDMA_RCM
            scraped_data=DDMA_RCM.main(scraped_data)    

        if InputParameters['PayorName'] == "Delta Dental New Hampshire":
            from wrapers import DDnortheastRCM
            scraped_data=DDnortheastRCM.main(scraped_data) 
    from wrapers import toolkitPP
    if InputParameters["AppName"]== "Payment Processing":
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
        if InputParameters['PayorName'] == "United Concordia":
            from wrapers import echo
            scraped_data=echo.main(scraped_data)
        if InputParameters['PayorName'] == "Aetna":
            from wrapers import aetnamaster
            scraped_data=aetnamaster.main(scraped_data)
        if InputParameters['PayorName'] == "Guardian":
            from wrapers import guardianWrapper
            scraped_data=guardianWrapper.main(scraped_data)


        if InputParameters['PayorName'] == "Managed Care of North America- MCNA":
            from wrapers import mcna
            scraped_data=mcna.main(scraped_data)
            
        for i, obj in enumerate(scraped_data['PpEobClaimDetail'], start=1):
            obj["RecordId"] = i
        for i, obj in enumerate(scraped_data['EFTPatients'], start=1):
            obj["RecordId"] = i
        for i, obj in enumerate(scraped_data['PpEobClaimMaster'], start=1):
            obj["RecordId"] = i

        [ctxt.update({'PPTransPayorListID': patient.get('PPTransPayorListID', ''), 
                      'RecordID' : str(uuid.uuid4())
                      }) 
                      for i in scraped_data for ctxt in scraped_data[i]]


    return scraped_data