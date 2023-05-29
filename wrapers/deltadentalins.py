import json
import re
import pandas as pd
from datetime import datetime
import sys
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from local import kickoff as kick

def TreatmentHistorySummary(treatmenthistory):
    df=pd.DataFrame(treatmenthistory)
    df3 = df.groupby(['ProcedureCode', 'ServiceDate'])['ToothCode'].apply(','.join).reset_index()
    def sort_date(servicedate):
        df1 = pd.DataFrame()
        count= 0
        for each in servicedate:
            each1sort = each.split(',')
            each1sort.sort(key=lambda date: datetime.strptime(date.strip(), "%m/%d/%Y"), reverse=True)
            new_row = {'ServiceDateSorted':','.join(each1sort)} 
            df2['ServiceDateSorted'] = pd.DataFrame(new_row, index=[0])
            df1 = pd.concat([df1,df2] , axis=0, ignore_index=True)
            count = count+1
        return df1

    summary_df = pd.DataFrame(columns=['ProcedureCode','ProcedureCodeDescription','LimitationText','LimitationAlsoAppliesTo','History'])
    df2 = pd.DataFrame()
    df2=sort_date(df.ServiceDate)
    df['ServiceDateSorted'] = df2
    unique_proc_code = df['ProcedureCode'].unique()
            
    for each_proc_code in unique_proc_code:
        df = df.drop_duplicates(subset=["ProcedureCode", "ServiceDate"], keep='first')
        each_loc = df[df.ProcedureCode == each_proc_code][['ServiceDateSorted','ToothCode', 'ServiceDate']].iloc
        data= {'ProcedureCode':each_proc_code, 'ProcedureCodeDescription':df[df.ProcedureCode == each_proc_code]['ProcedureCodeDescription'].iloc[0],
            'LimitationText':df[df.ProcedureCode == each_proc_code]['LimitationText'].iloc[0],
            'LimitationAlsoAppliesTo': df[df.ProcedureCode == each_proc_code]['LimitationAlsoAppliesTo'].iloc[0]}

        historytext = ''
        for each in each_loc:
            for each_date in each.ServiceDateSorted.split(','):
                toothcode = ''
                #historytext = (historytext + each_date + toothcode.strip())
                toothcode = ''.join(df3[(df3['ProcedureCode'] == each_proc_code) & (df3['ServiceDate'] == each.ServiceDate)]['ToothCode'])
                if len(each.ToothCode)!=0: 
                    historytext = (historytext + each_date + ':'+ f"({toothcode})")
                else:
                    historytext = (historytext + each_date) 
                
        data['History'] = historytext.strip(",")
        df_2 = pd.DataFrame(data,index=[1])
        summary_df = pd.concat([summary_df,df_2])           
        
        # reset index
        summary_df.reset_index(drop=True, inplace=True)
        
    return summary_df.to_dict("records")
def addressmaker(address):
  address = address.split("\n")
  address.remove("Claim mailing address")
  for ads in address:
    if ads.startswith("Claim payer ID"):
      ClaimPayerID=ads.split(":")[-1].strip()
     
      address.remove(ads)
  ClaimMailingAddress=" ".join(address)
 
  return ClaimMailingAddress,ClaimPayerID

def OONBenefits(benefits):
    for obj in benefits:
        if obj["NonDeltaDentalDentist(Benefitsbasedoncontractallowance)ContractBenefitLevel"]!="":
            return "Yes"
        else:
            return "No"


def FamilyCalenderDeductible(Deductibles):
    if len(Deductibles)!=0:
        
        for obj in Deductibles:
            if obj['Type'] =="Calendar Family Deductible":
                return  float(obj['Amount'].replace("$",""))
    else:
        return None        
def FamilyDeductibleMet(Deductibles):
    if len(Deductibles)!=0:
        for obj in Deductibles:
            if obj['Type'] =="Calendar Family Deductible":
                return   float(obj['Amount'].replace("$","")) - float(obj['Remaining'].replace("$",""))
    else:
        return None
def IndividualAnnualDeductible(Deductibles):
    for obj in Deductibles:
        if obj['Type'] =="Calendar Individual Deductible":
            return  float(obj['Amount'].replace("$",""))
            
def IndividualDeductibleMet(Deductibles):
    for obj in Deductibles:
        if obj['Type'] =="Calendar Individual Deductible":
            return   float(obj['Amount'].replace("$","")) - float(obj['Remaining'].replace("$",""))
        
def AdultOrthodonticCovered(agelimitation):
    
    for obj in agelimitation:
        if obj['AgeLimit'] =='No Age Limit':
            return "Yes"
        if int(''.join(filter(str.isdigit, obj['AgeLimit'])))   <18:
            return "No"
        else:
            "Yes"
def LifetimeMaximumBenefits(maximums):
    for obj in maximums:
        if obj['Type'] =='Lifetime Individual Maximum':
            return  float(obj['Amount'].replace("$",""))
        
def BenefitsUsedtoDate(maximums):
     for obj in maximums:
        if obj['Type'] =='Lifetime Individual Maximum':
            return   float(obj['Amount'].replace("$","")) -  float(obj['Remaining'].replace("$",""))
        
def RemainingBenefitAvailable(maximums):
    for obj in maximums:
        if obj['Type'] =='Lifetime Individual Maximum':
            return  float(obj['Remaining'].replace("$",""))
        
def  cob(EligibilityOtherProvisions):
    data=EligibilityOtherProvisions.get('CobRule')
    if data:
        CoordinationofBenefitsType =data
        CoordinationofBenefits    ="Yes" 
        return CoordinationofBenefitsType,CoordinationofBenefits
    else:
        CoordinationofBenefitsType ="No"
        CoordinationofBenefits     =""
        return CoordinationofBenefitsType,CoordinationofBenefits
               
        
def AgelimitShow(age_obj):
    if len(age_obj)!=0:
        string=""
        for obj in age_obj:
            memeber=obj['FamilyMember']
            limit   =obj['AgeLimit']
            string+=f"{memeber} : {limit}\n"
        return string.strip("\n")  
    else:
        return None
        
        
    
            
     

def WaitingPeriods(waiting_periods):
    
    count = 0
    for i in waiting_periods:
        if all(value == "" for value in i.values()):
            count += 1
            
    if len(waiting_periods) == count:
        return "No"
    else:
        return "Yes"
def Orthodontic(maximums):
    if  len(maximums)!=0:
        for obj in maximums:
            if obj['Type'] =='Lifetime Individual Maximum':
                if "Orthodontics".lower() in  obj['ProgramMaximum_AppliesToTheFollowingServices_'].lower():
                    OrthodonticIndividualLifetimeBenefit ="Yes"
                    amount=float(obj['Amount'].replace("$",""))
                    remaining=float(obj['Remaining'].replace("$",""))
                    return OrthodonticIndividualLifetimeBenefit , amount , remaining
            else:
                return None, None, None   
    else:
        return None, None, None 
                     

def DeductibleApplicable(Benefits):
    if len(Benefits)!=0:
        for obj in Benefits:
        
            if obj['DeltaDentalPPOTMDentistContractBenefitLevel'].endswith("1"):
                print(obj['DeltaDentalPPOTMDentistContractBenefitLevel'])
            
                obj['DeductibleApplicable'] ="Yes"
            else:
                obj['DeductibleApplicable'] ="No"
                
            for i in obj:
                
                if "%" in obj[i]:
                
                    obj[i] =obj[i].split("%")[0]+"%"
                
        return Benefits
    else:
        return  None       
            
def AnnualMaximumBenefits(maximums):
    if len(maximums)!=0:
        for obj in maximums:
            if obj['Type'] =='Calendar Individual Maximum':
                return  float(obj['Amount'].replace("$",""))
    else:
        return None    
def AnnualBenefitsUsedtoDate(maximums):
     if len(maximums)!=0:
        for obj in maximums:
            if obj['Type'] =='Calendar Individual Maximum':
                return   float(obj['Amount'].replace("$","")) -  float(obj['Remaining'].replace("$",""))
     else:
         return None       
        
def AnnualRemainingBenefitAvailable(maximums):
    if len(maximums) != 0:
        for obj in maximums:
            if obj['Type'] =='Calendar Individual Maximum':
                return  float(obj['Remaining'].replace("$",""))  
    return None     
            
def limitationsSoter(benefits,proccodes):
    
    CodesRequireScraping=[]
    for obj in benefits:
        if obj['procedureCode'] in proccodes:
            if "[Limitations Apply]" in obj['limitation']:
                CodesRequireScraping.append(obj['procedureCode'] )
    return CodesRequireScraping            
                
def limitationsUpdater(limitations,benefits):
    result = {}
    for d in limitations:
        result.update(d)
    for obj in limitations:
        
        obj=list(obj.keys())[0]
        for j in benefits:
            if j['procedureCode'].lower() ==obj.lower():
                finaltext =""
                for k in result[obj]:
                    limitationstxt = k['Limitation']
                    Age             = k['Age']
                    tooth_code      = k['ToothCode']
                    if len(tooth_code)==0:
                        tooth_code="N/A "
                    if len(Age)==0:
                        Age  ="N/A"
                    finaltext+=f"Limitations: {limitationstxt},  Age limitation: {Age}, Tooth_code: {tooth_code}\n"
                finaltext=finaltext.strip("\n").strip()        
                j['limitation']=j['limitation'].replace("[Limitations Apply]",f" {finaltext}")    
    return  benefits          
def limitationsUpdaterTreatmentHistory(limitations,benefits):
    result = {}
    for d in limitations:
        result.update(d)
    for obj in limitations:
        
        obj=list(obj.keys())[0]
        for j in benefits:
          
            if j['ProcedureCode'].lower() ==obj.lower():
                finaltext =""
                for k in result[obj]:
                    limitationstxt = k['Limitation']
                    Age             = k['Age']
                    tooth_code      = k['ToothCode']
                    if len(tooth_code)==0:
                        tooth_code="N/A "
                    if len(Age)==0:
                        Age  ="N/A "                        
                    finaltext+=f"Limitations: {limitationstxt},  Age limitation: {Age}, Tooth_code: {tooth_code}\n"
                finaltext=finaltext.strip("\n").strip()     
                j['LimitationText']=j['LimitationText'].replace("[Limitations Apply]",f" {finaltext}")    
    return  benefits                          
def getrequestprocodes(request):
    codes=request['InputParameters'].get('ProcCodes')
    if codes!=None:
        return codes                                         
    else:
        return []                  
    
def main(data,request=None):
    EligibilityPatientVerification={}
    if data.get('EligibilityPatientVerification'):
        EligibilityPatientVerification             = data.get("EligibilityPatientVerification")
        if EligibilityPatientVerification:
            EligibilityPatientVerification =EligibilityPatientVerification[0]

    EligibilityMaximums =[]        
    if data.get("EligibilityMaximums"):
        EligibilityMaximums                        = data["EligibilityMaximums"]
        
    EligibilityDeductiblesProcCode=[]
    if data.get("EligibilityDeductiblesProcCode"):
        EligibilityDeductiblesProcCode             = data["EligibilityDeductiblesProcCode"]
        
    EligibilityServiceTreatmentHistory=[]
    if data.get("EligibilityServiceTreatmentHistory"):
        EligibilityServiceTreatmentHistory         = data["EligibilityServiceTreatmentHistory"]
        
    EligibilityBenefits=[]   
    if data.get('EligibilityBenefits'):
        EligibilityBenefits                        = data["EligibilityBenefits"]
        
    EligibilityAgeLimitation =[]
    if data.get("EligibilityAgeLimitation"):
        EligibilityAgeLimitation                   = data["EligibilityAgeLimitation"]
        
    EligibilityOtherProvisions={}
    if data.get("EligibilityOtherProvisions"):
        EligibilityOtherProvisions                 = data["EligibilityOtherProvisions"][0]
        
    EligibilityPayorAddressDetails =None    
    if EligibilityPatientVerification:
        if len(EligibilityPatientVerification)!=0:
            EligibilityPayorAddressDetails             = data["EligibilityPatientVerification"][0].get('Address')
    EligibilityFamilyMembersWaitingPeriods=None
    if data.get("EligibilityFamilyMembersWaitingPeriods"):
        EligibilityFamilyMembersWaitingPeriods     = data["EligibilityFamilyMembersWaitingPeriods"]
    
    ClaimMailingAddress= None
    ClaimPayerID       = None
    if EligibilityPayorAddressDetails!=None:
        ClaimMailingAddress,ClaimPayerID                                  = addressmaker(EligibilityPayorAddressDetails)
    
    OONBenefits_=None        
    if len(EligibilityBenefits)!=0:
        OONBenefits_                                                      = OONBenefits(EligibilityBenefits)
        
    IndividualAnnualDeductible_=None
    IndividualDeductibleMet_=None
    if len(EligibilityDeductiblesProcCode)!=0:
        IndividualAnnualDeductible_                                       = IndividualAnnualDeductible(EligibilityDeductiblesProcCode)
    
        IndividualDeductibleMet_                                          = IndividualDeductibleMet(EligibilityDeductiblesProcCode)
    AdultOrthodonticCovered_=None    
    if len(EligibilityAgeLimitation)!=0 and len(EligibilityOtherProvisions)!=0:
        AdultOrthodonticCovered_                                          = "N/A" if EligibilityOtherProvisions["OrthodonticAgeLimit"]=="N/A" else  AdultOrthodonticCovered(EligibilityAgeLimitation)
    LifetimeMaximumBenefits_=None    
    BenefitsUsedtoDate_=None
    RemainingBenefitAvailable_=None
    if len(EligibilityMaximums)!=0:
        LifetimeMaximumBenefits_                                          =  LifetimeMaximumBenefits(EligibilityMaximums)
    
        BenefitsUsedtoDate_                                               =  BenefitsUsedtoDate(EligibilityMaximums)
    
        RemainingBenefitAvailable_                                        = RemainingBenefitAvailable(EligibilityMaximums)
    
    EligibilityPatientVerification['OrthodonticPayment']              = EligibilityOtherProvisions.get('OrthodonticPayment')

    CoordinationofBenefitsType,CoordinationofBenefits                 =     cob(EligibilityOtherProvisions)
    if EligibilityFamilyMembersWaitingPeriods!=None:
        EligibilityFamilyMembersWaitingPeriods_                           =       WaitingPeriods(EligibilityFamilyMembersWaitingPeriods)
    else:
        EligibilityFamilyMembersWaitingPeriods_=None    
    EligibilityPatientVerification['DependentChildCoveredAgeLimit']   =     EligibilityOtherProvisions.get('ChildCoveredToAge')
    EligibilityPatientVerification["DependentStudentAgeLimit"]        =     EligibilityOtherProvisions.get('StudentCoveredToAge')
    EligibilityPatientVerification["ClaimMailingAddress"]             =      ClaimMailingAddress
    
    EligibilityPatientVerification['ClaimPayerID']                    =      ClaimPayerID
    
    EligibilityPatientVerification['oonBenefits']                     =      OONBenefits_
    
    EligibilityPatientVerification['IndividualAnnualDeductible']      =      IndividualAnnualDeductible_
    
    EligibilityPatientVerification['IndividualDeductibleMet']         =      IndividualDeductibleMet_
    
    EligibilityPatientVerification['LifetimeMaximumBenefits']         =      LifetimeMaximumBenefits_
    
    EligibilityPatientVerification['LifetimeBenefitsUsedtoDate']              =      BenefitsUsedtoDate_
    
    EligibilityPatientVerification['LifetimeRemainingBenefitAvailable']       =      RemainingBenefitAvailable_
    
    EligibilityPatientVerification['CoordinationofBenefits']          =      CoordinationofBenefits
    
    EligibilityPatientVerification['CoordinationofBenefitsType']      =      CoordinationofBenefitsType
    
    EligibilityPatientVerification['AdultOrthodonticCovered']         =      AdultOrthodonticCovered_
    
    
  #  EligibilityPatientVerification['BenefitsPaid']                    =      BenefitsPaid_
    EligibilityPatientVerification['FamilyMembersWaitingPeriods']     =      EligibilityFamilyMembersWaitingPeriods_
    
    
    OrthodonticLifetimeBenefit ,OrthodonticMaximumBenefit,OrthodonticRemainingBenefit =Orthodontic(EligibilityMaximums)
    EligibilityPatientVerification['OrthodonticLifetimeBenefit']     =       OrthodonticLifetimeBenefit
    EligibilityPatientVerification['OrthodonticMaximumBenefit']      =       OrthodonticMaximumBenefit
    EligibilityPatientVerification['OrthodonticRemainingBenefit']    =       OrthodonticRemainingBenefit
    EligibilityPatientVerification['FamilyCalenderDeductible']       =       FamilyCalenderDeductible(EligibilityDeductiblesProcCode)
    EligibilityPatientVerification['FamilyCalenderDeductibleMet']    =        FamilyDeductibleMet(EligibilityDeductiblesProcCode)
    
    EligibilityPatientVerification['AnnualMaximumBenefits'] = AnnualMaximumBenefits(EligibilityMaximums)
    EligibilityPatientVerification["AnnualBenefitsUsedtoDate"] = AnnualBenefitsUsedtoDate(EligibilityMaximums)
    EligibilityPatientVerification["AnnualRemainingBenefitAvailable"] = AnnualRemainingBenefitAvailable(EligibilityMaximums)
    
    EligibilityPatientVerification["SpecialistOfficeVisitCopay"] = None
    EligibilityPatientVerification["IsReferralNeeded"] = None
    EligibilityPatientVerification["PreCertRequired"] = None
    EligibilityPatientVerification["TreatmentinProgressCoverage"] = None
    EligibilityPatientVerification["PreauthorizationRequired"] = None
    EligibilityPatientVerification["MedicallyNecessaryonly"] = None
    EligibilityPatientVerification["AutomaticPayments"] = None
    EligibilityPatientVerification["ContinuationClaimNeeded"] = None
    
    EligibilityPatientVerification['OrthodonticAgeLimits']               =  AgelimitShow(EligibilityAgeLimitation)
   # EligibilityPatientVerification["FrequencyLimitationsExclusions"] = None
   # EligibilityPatientVerification["ExclusionsAgeRestrictionsMaximums"] = None
    if len(EligibilityBenefits)!=0:
        EligibilityBenefits                     =  DeductibleApplicable(EligibilityBenefits)
    data["EligibilityBenefits"]= EligibilityBenefits
    

    request_procodes=getrequestprocodes(request)
    print(request_procodes)
    if len(request_procodes)!=0:
        limitationsProCodes=limitationsSoter(EligibilityBenefits,request_procodes)
        print(limitationsProCodes,"here")
        if len(limitationsProCodes)!=0:
            
        
            for i in request['Xpaths']:
                if i['DataContextName'] =='Eligibilitylimitaiton':
                    print(list(set(limitationsProCodes)))
                    data_=json.loads(i['XPath'])
                    data_['Xpaths'][0]['MultiplElements']['multiple_elements_xpath']=list(set(limitationsProCodes))
                    i['XPath']=json.dumps(data_)
                    
                    
                    
        
            request['Xpaths']=[x for x in request['Xpaths'] if  x['DataContextName']  in  ['EligibilityLogin','Eligibilitylimitaiton'] ]
            limit=kick(request,"sher")
            data['Eligibilitylimitaiton']=        limit['Eligibilitylimitaiton']
            print(limit)
            
            if len(EligibilityBenefits)!=0:
                data["EligibilityBenefits"]=limitationsUpdater(data['Eligibilitylimitaiton'],EligibilityBenefits)
            
            if len(data["EligibilityServiceTreatmentHistory"])!=0:
                data['EligibilityServiceTreatmentHistory']=limitationsUpdaterTreatmentHistory(data['Eligibilitylimitaiton'],data["EligibilityServiceTreatmentHistory"])
    if len(data["EligibilityServiceTreatmentHistory"])!=0:
        data['TreatmentHistorySummary']=TreatmentHistorySummary(data['EligibilityServiceTreatmentHistory'])    
    try:
        del data["EligibilityPatientVerification"][0]['Address']
    except:
        pass
    try:
        del data['Eligibilitylimitaiton']
    except:
        pass    
    return data
