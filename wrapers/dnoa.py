def calculate_difference(a,b):
    a=a.replace(",", "").replace("N/A", "0").replace("$", "")
    b=b.replace(",", "").replace("N/A", "0").replace("$", "")
    return float(a)-float(b)
def mapdicts(a,b):
    for x in a:
        # if(a.get(x)==None):
        #     b.update({x:None})
        b.update({x:""})
    return b
def check_oon_flag(temp):
    for x in temp:
        try:
            if(float(temp.get(x).get("OutOfNetworkindividual").replace(",", "").replace("N/A", "0").replace("$", ""))):
                return "Yes"
        except: pass
    return "No"
def generate_codelist(tempdict):
    text=tempdict.get("FrequencyLimitations").replace("\n", "")
    codelist=[]
    for x in range(len(text)):
        if(text[x]=="D" and text[x+1].isnumeric()):
            code="D"
            for y in text[x+1:]:
                if(not y.isnumeric() and y!="-"):  break
                code+=y
            x=x+len(code)
            codelist.append(code)
    x=0

    
    while x<len(codelist)-1:
        if(codelist[x][-1]=="-"):
            
            
            codelist[x]=codelist[x].replace("-", "")
            
            for y in range(int(codelist[x][1:])+1, int(codelist[x+1][1:])):
                if(y<10): codelist.insert(x+1, f"D000{y}")
                elif(y<100): codelist.insert(x+1, f"D00{y}")
                elif(y<1000): codelist.insert(x+1, f"D0{y}")
                elif(y<10000): codelist.insert(x+1, f"D{y}")
                x+=1
            x+=1
        x+=1
    
    return codelist

def get_related_codes(code, master_codelist):
    temp=[]
    for codelist in master_codelist:
        for x in codelist:
            if(x==code):
                codelist=list(set(codelist))
                codelist.remove(x)
                temp.extend(codelist)
                break
    temp=str(list(set(temp)))[1:-1].replace("'", "")
    return temp

def getbenefitsdata(code, templist):
    for x in templist:
        if(x.get("procedureCode")==code):
            return x.get("Category"), x.get("limitation")
    return "", ""
def fixdate(text):
    t=""
    for x in text.split('/'): 
        t+=x.zfill(2)+"/"
    return t[:-1]
def main(data):
    output={}
    PDFData={}
    tempmapdict={
            "EnrolleeName": "Arnulfo Saucedo",
            "DateOfBirth": "02/14/1984",
            "EnrolleeId": "Z62TN21C",
            "PlanName": "THE UNIVERSITY OF TEXAS - UT DALLASSW-P",
            "PlanNumber": "05968 - 02501",
            "EffectiveDate": "09/01/2008",
            "EndDate": "",
            "EligibilityStatus": "Active",
            "ProgramType": "DPO",
            "FamilyMemberName": "Alexander Saucedo",
            "FamilyMemberEffectiveDate": "09/01/2016",
            "FamilyMemberId": "005168027904",
            "FamilyMemberEndDate": "",
            "FamilyMemberDateOfBirth": "09/22/2015",
            "FamilyMemberEligibilityStatus": "Active",
            "OrthodonticPayment": "Following the initial claim payment, orthodontic payments will be made on a monthly basis until the plan maximum has been reached. Payments cease with the enrollment end date.",
            "DependentChildCoveredAgeLimit": "26 (Division has no rule)",
            "DependentStudentAgeLimit": "26 (Division has no rule)",
            "ClaimMailingAddress": "Delta Dental Insurance Company PO box 1809 Alpharetta, GA 30023-1809",
            "ClaimPayerID": "94276",
            "oonBenefits": "Yes",
            "IndividualAnnualDeductible": None,
            "IndividualDeductibleMet": None,
            "LifetimeMaximumBenefits": 3000.0,
            "LifetimeBenefitsUsedtoDate": 0.0,
            "LifetimeRemainingBenefitAvailable": 3000.0,
            "CoordinationofBenefits": "Yes",
            "CoordinationofBenefitsType": "Standard: Coordination of benefits is calculated by the lesser of the two, either OIC remaining allowed amount or the secondary plan\u2019s liability.",
            "AdultOrthodonticCovered": "Yes",
            "FamilyMembersWaitingPeriods": "No",
            "OrthodonticLifetimeBenefit": "Yes",
            "OrthodonticMaximumBenefit": 3000.0,
            "OrthodonticRemainingBenefit": 3000.0,
            "FamilyCalenderDeductible": None,
            "FamilyCalenderDeductibleMet": None,
            "AnnualMaximumBenefits": None,
            "AnnualBenefitsUsedtoDate": None,
            "AnnualRemainingBenefitAvailable": None,
            "SpecialistOfficeVisitCopay": None,
            "IsReferralNeeded": None,
            "PreCertRequired": None,
            "TreatmentinProgressCoverage": None,
            "PreauthorizationRequired": None,
            "MedicallyNecessaryonly": None,
            "AutomaticPayments": None,
            "ContinuationClaimNeeded": None,
            "OrthodonticAgeLimits": "Child and Adult : No Age Limit"
        }
    PDFData=mapdicts(tempmapdict, PDFData)
    PDFData.update({"InsuranceName":data.get('EligibilityPatientVerification')[-1].get('Payer')})
    for key in data.get('EligibilityPatientVerification')[-1]:
        if(key.startswith("ClaimsAddress")):
            PDFData.update({"InsuranceMailingAddress":key[13:]+data.get('EligibilityPatientVerification')[-1].get(key).replace("Address1", "")})
            PDFData.update({"ClaimMailingAddress":key[13:]+data.get('EligibilityPatientVerification')[-1].get(key).replace("Address1", "")})
            break
    PDFData.update({"ClaimPayerID":data.get('EligibilityPatientVerification')[-1].get('PayerId')})
    PDFData.update({"EffectiveDate":data.get('EligibilityPatientVerification')[1].get('Enrolled')})
    PDFData.update({"PlanName":data.get('EligibilityPatientVerification')[-1].get('GroupName')})
    PDFData.update({"PlanNumber":data.get('EligibilityPatientVerification')[-1].get('GroupNumber')})
    
    planinfodict={}
    EligibilityMaximums=[]
    EligibilityDeductiblesProcCode=[]
    for temp1 in data.get('EligibilityMaximums'):
        if("Maximum" in temp1.get("Type")): 
            tempmapdict={
                "Type": "Lifetime Individual Maximum",
                "ProgramMaximum_AppliesToTheFollowingServices_": "Oral & Maxillofacial SurgeryOrthodontics",
                "Network": "Delta Dental DPO DentistDelta Dental Premier DentistNon-Delta Dental Dentist (Benefits based on contract allowance)",
                "Amount": "$3000.00",
                "Remaining": "$3000.00"
            }
            temp2={}
            temp2=mapdicts(tempmapdict, temp2)
            temp2.update(temp1)
            EligibilityMaximums.append(temp2)
        elif("Deductible" in temp1.get("Type")): 
            tempmapdict={
                "Type": "",
                "ProgramDeductible_AppliesToTheFollowingServices_": "",
                "Network": "",
                "Amount": "",
                "Remaining": ""
            }
            temp2={}
            temp2=mapdicts(tempmapdict, temp2)
            temp2.update(temp1)
            EligibilityDeductiblesProcCode.append(temp2)
        planinfodict.update({temp1.get("Type"):temp1})

    PDFData.update({"oonBenefits":check_oon_flag(planinfodict)})
    
    PDFData.update({"IndividualAnnualDeductible":planinfodict.get("Deductible - Benefit Period").get("InNetworkindividual")})
    PDFData.update({"IndividualDeductibleMet":calculate_difference(planinfodict.get("Deductible - Benefit Period").get("InNetworkindividual"), planinfodict.get("Deductible - Benefit Period Remaining").get("InNetworkindividual"))})

    PDFData.update({"IndividualAnnualDeductible":planinfodict.get("Deductible - Benefit Period").get("InNetworkfamily")})
    PDFData.update({"CalenderFamilyDeductibleMet":calculate_difference(planinfodict.get("Deductible - Benefit Period").get("InNetworkfamily"), planinfodict.get("Deductible - Benefit Period Remaining").get("InNetworkfamily"))})

    PDFData.update({"LifetimeMaximumBenefits":planinfodict.get("Maximums - Lifetime").get("InNetworkindividual")})
    PDFData.update({"BenefitsUsedToDate":calculate_difference(planinfodict.get("Maximums - Lifetime").get("InNetworkindividual"), planinfodict.get("Maximums - Lifetime Remaining").get("InNetworkindividual"))})

    PDFData.update({"RemainingBenefitAvailable":planinfodict.get("Maximums - Lifetime Remaining").get("InNetworkindividual")})
    PDFData.update({"AnnualMaximumBenefits":planinfodict.get("Maximums - Benefit Period").get("InNetworkindividual")})
    PDFData.update({"BenefitsUsedToDate":calculate_difference(planinfodict.get("Maximums - Benefit Period").get("InNetworkindividual"), planinfodict.get("Maximums - Benefit Period Remaining").get("InNetworkindividual"))})
    PDFData.update({"RemainingBenefitAvailable":planinfodict.get("Maximums - Benefit Period Remaining").get("InNetworkindividual")})

    PDFData.update({"MissingToothClause":data.get('EligibilityPatientVerification')[2].get('MissingToothProvision')})
    PDFData.update({"CoordinationOfBenefits":data.get('EligibilityPatientVerification')[2].get('CoordinationOfBenefits')})
    
    waitingperiods={}
    ProcedureCode=[]
    master_codelist=[]
    for templist in data.get('EligibilityBenefits'):
        for tempdict in templist:
            if(tempdict.get("Category")):
                if(tempdict.get("Category")=="Orthodontics"):
                    try:
                        PDFData.update({"OrthodonticMaximumBenefit":templist[0].get("InNetworkindividual")})
                        PDFData.update({"OrthodonticRemainingBenefit":templist[1].get("InNetworkindividual")})
                    except:
                        PDFData.update({"OrthodonticMaximumBenefit":""})
                        PDFData.update({"OrthodonticRemainingBenefit":""})
                    
                waitingperiods.update({f'{tempdict.get("Category")}WaitingPeriod'.replace(" ", ""): tempdict.get("WaitingPeriod")})
                codelist=generate_codelist(tempdict)
                master_codelist.append(codelist)
                for code in codelist:
                    try: 
                        # abc=ProcedureCode.get(code)
                        # abc.extend([tempdict])
                        # ProcedureCode.update({code:abc})
                        abc={}
                        tempmapdict={
                            "procedureCode": "D0120",
                            "procedureCodeDescription": "Periodic oral evaluation - established patient",
                            "limitation": "Benefit is limited to two of any oral evaluation procedure within the contract period. Comprehensive evaluations are limited to once per provider.",
                            "PreApproval": "No",
                            "DeductibleApplicable": "No"
                        }
                        abc=mapdicts(tempmapdict, abc)
                        abc.update({"procedureCode":code})
                        abc["limitation"] = tempdict["FrequencyLimitationText"]
                        abc.update(tempdict)
                        
                        ProcedureCode.append(abc)
                    except: 
                        ProcedureCode.update({code:[tempdict]})
    # abc=[]
    # for tempdict in ProcedureCode:
    #     abc.append({tempdict:ProcedureCode.get(tempdict)})

    
    PDFData.update(waitingperiods)
    
    
    temp=PDFData
    # temp.update(data.get("EligibilityPatientVerification")[0])
    x=data.get("EligibilityPatientVerification")[0]
    temp.update({"EligibilityStatus":x.get("MemberStatus")})
    temp.update({"EnrolleeName":x.get("SubscriberName").replace(" Information cannot be retrieved at this time", "")})
    temp.update({"DateOfBirth":x.get("DateOfBirth")})
    temp.update({"EnrolleeId":x.get("SubscriberId")})
    temp.update({"FamilyMemberName":x.get("MemberName")})
    

    # temp.update(data.get("EligibilityPatientVerification")[1])
    x=data.get("EligibilityPatientVerification")[1]
    temp.update({"FamilyMemberEffectiveDate":x.get("Enrolled")})
    # temp.update({"EligibilityStatus":x.get("MemberStatus")})
    # temp.update({"EligibilityStatus":x.get("MemberStatus")})

    # temp.update(data.get("EligibilityPatientVerification")[2])
    x=data.get("EligibilityPatientVerification")[2]
    temp.update({"FamilyMemberEffectiveDate":x.get("AlternativeBenefitProvision")})
    temp.update({"FamilyMemberEffectiveDate":x.get("MissingToothProvision")})
    temp.update({"CoordinationofBenefitsType":x.get("CoordinationOfBenefits")})
    temp.update({"FamilyMemberEffectiveDate":x.get("AssignmentOfBenefits")})
    temp.update({"FamilyMemberEffectiveDate":x.get("FillingDowngrade")})

    temp.update(data.get("EligibilityPatientVerification")[-1])
    
    output.update({"EligibilityPatientVerification":[temp]})
    output.update({"EligibilityMaximums":EligibilityMaximums})
    output.update({"EligibilityDeductiblesProcCode":EligibilityDeductiblesProcCode})
    output.update({"EligibilityBenefits": ProcedureCode})
    EligibilityServiceTreatmentHistory=[]
    for x in data.get("EligibilityServiceTreatmentHistory"):
        tempmapdict={
            "ProcedureCode": "D0120",
            "ProcedureCodeDescription": "Periodic oral evaluation - established patient",
            "LimitationText": "Benefit is limited to two of any oral evaluation procedure within the contract period. Comprehensive evaluations are limited to once per provider.",
            "LimitationAlsoAppliesTo": "D0145, D0150, D0160, D0180, D0190, D0191, D9310",
            "ServiceDate": "12/09/2022, 06/24/2022, 12/17/2021, 07/05/2021, 01/04/2021, 07/24/2020, 01/03/2020, 07/26/2019, 12/21/2018, 05/25/2018, 11/21/2017",
            "ToothCode": "",
            "ToothDescription": "",
            "ToothSurface": ""
        }
        temp={}
        temp=mapdicts(tempmapdict, temp)
        temp.update({"ProcedureCode": x.get("ProcedureCode")})
        temp.update({"ToothCode": x.get("Tooth_Quadrant")})
        temp.update({"ToothSurface": x.get("Surfaces")})
        temp.update({"ProcedureCodeDescription": x.get("Description")})
        temp.update({"ServiceDate": fixdate(x.get("DateOfService"))})
        EligibilityServiceTreatmentHistory.append(temp)
    output.update({"EligibilityServiceTreatmentHistory":EligibilityServiceTreatmentHistory})
    GROUPINFO=[]
    temp={}
    for x in data.get("EligibilityPatientVerification"):
        if(x.get("Status")==""):
            temp={"Name":x.get("Name/Plans")}
        elif(x.get("Status")!=None):
            temp.update({"Plan":x.get("Name/Plans"), "Status":x.get("Status")})
            GROUPINFO.append(temp)
            temp={}
    output.update({"AssociatedMember":GROUPINFO})
    temp=[]
    for y in data.get("EligibilityServiceTreatmentHistory"):
        History=""
        for x in data.get("EligibilityServiceTreatmentHistory"):
            code=y.get("ProcedureCode")
            relatedcodes=get_related_codes(code, master_codelist)
            if(x.get("DateOfService") not in History):
                if(x.get('Tooth_Quadrant')!=""):
                    History+=f' {fixdate(x.get("DateOfService"))}:({x.get("Tooth_Quadrant")})'
                else:
                    History+=f' {fixdate(x.get("DateOfService"))}'
            
            ProcedureCodeDescription, LimitationText=getbenefitsdata(code, ProcedureCode)
        temp.append({"ProcedureCode":code, "ProcedureCodeDescription":ProcedureCodeDescription, "LimitationText":LimitationText , "LimitationAlsoAppliesTo":relatedcodes, "History":History.strip()})
    output.update({"TreatmentHistorySummary":temp})   
    output.update({"EligibilityAgeLimitation": [
        {
            "FamilyMember": "",
            "AgeLimit": ""
        }
    ]})
    # output.update({"EligibilityPlanInformation":data.get("EligibilityPlanInformation")})
    return output
                
                



# import json
# data=json.load(open("C:\\Users\\saran\\Downloads\\SD Payor Scraping\\output.json", 'r'))
# output=main(data)
# with open("newres1.json", "w") as outfile:
#     json.dump(output, outfile, indent=4)