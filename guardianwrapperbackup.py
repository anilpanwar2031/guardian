import pdfplumber
import tika

tika.initVM()

from pprint import pprint

from Utilities.pdf_utils import *
from FileDownload import Downloader

import tabula
import pandas as pd
from PyPDF2 import PdfReader

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import json
from FileDownload import Downloader
import random, string
import tabula
import sys
import os
import uuid


def getAllTexts(file_path):
    texts = ' '
    with open(file_path, 'rb') as file:
        # Create a PdfReader object
        pdf = PdfReader(file)

        for page in pdf.pages:
            text = page.extract_text()
            texts = texts + text + ' '
    return texts


def getRemarks(texts, claimnumber):
    remarks = ''
    remarks = texts.split(f"Remarks for claim # {claimnumber}:")[1]

    if '10 Hudson' in remarks:
        remarks = remarks.split('10 Hudson')[0]
    if 'SCHEDULE' in remarks:
        remarks = remarks.split('SCHEDULE')[0] + 'SCHEDULE'
    if 'Comments' in remarks:
        remarks = remarks.split('Comments:')[0]

    print("RRMMMMM", claimnumber, remarks)

    return remarks.replace('\n', ' ').replace("  ", " ").strip()


def getBenefit(texts, claimnumber):
    benefit = texts.split(f"Remarks for claim # {claimnumber}:")[0]
    benefit_dict = {}
    if 'Remarks for claim' in benefit:
        benefit = benefit.split('Remarks for claim')[1]

    adjustments = '$' + benefit.split('ADJUSTMENTS')[1].split('TOTAL BENEFIT PAID')[0].replace('\n', '').split('$')[1]

    benefit_dict['PaidByOtherInsurance'] = '$' + \
                                           benefit.split('PAID BY OTHER INSURANCE')[1].split('ADJUSTMENTS')[0].replace(
                                               '\n', '').split('$')[1]
    benefit_dict['TotalBenefitPaid'] = '$' + benefit.split('TOTAL BENEFIT PAID')[1].split('PATIENT')[0].replace('\n',
                                                                                                                '').split(
        '$')[1]
    benefit_dict['TotalPatientResp'] = '$' + benefit.split('PATIENT')[1].split('TOTALS\nTOTAL BENEFIT')[0].replace('\n',
                                                                                                                   '').split(
        '$')[1].strip()
    benefit_dict['TotalBenfitPayable'] = benefit.split('PAID BY OTHER INSURANCE')[0].split('\n')[-2].strip()
    benefit_dict['HigherAllowable'] = '$' + \
                                      benefit.split('BENEFIT SUMMARY')[1].split('HIGHER ALLOWABLE')[0].replace('\n',
                                                                                                               '').split(
                                          '$')[1].strip()
    return benefit_dict, adjustments


def process_tabula_address(tabula_df: pd.DataFrame) -> str:
    col_name: str = tabula_df.columns[0]
    item: str = f"{col_name} {' '.join(tabula_df[col_name].to_list())}"
    return item


def other_details(file_path):
    tabula_dfs = tabula.read_pdf(file_path, guess=False, pages=1, stream=True, encoding="utf-8",
                                 area=(97, 288, 152, 570), multiple_tables=True)
    string_to_find = "Provider"
    a = 0
    for key, value in tabula_dfs[0].items():
        if string_to_find in str(key) or string_to_find in str(value):
            a = 1
    if a:
        tab = tabula_dfs[0]
    else:
        tabula_dfs = tabula.read_pdf(file_path, guess=False, pages=2, stream=True, encoding="utf-8",
                                     area=(96, 287, 153, 572), multiple_tables=True)
        tab = tabula_dfs[0]

    df = tab
    df = df.T.reset_index()
    df.columns = df.iloc[0]
    dit = df[1:].reset_index(drop=True).to_dict(orient='records')[0]
    other_dict = {}
    other_dict['Provider'] = dit['Provider:']
    other_dict['RenderingProvider'] = dit['Provider:']
    other_dict['EFT_CheckDate'] = dit['Date:']
    other_dict['EFT_CheckNumber'] = dit['Check No.:']
    other_dict['TotalAmount'] = dit['Payment Amount:']

    return other_dict


def get_basic_details(file_path):
    tabula_dfs = tabula.read_pdf(file_path, guess=False, pages=1, stream=True, encoding="utf-8",
                                 area=[(141, 43, 176, 217), (25, 90, 53, 213), (97, 288, 152, 570)],
                                 multiple_tables=True)
    payee_address = process_tabula_address(tabula_dfs[0])
    payee_address_details = extract_address_details(payee_address)

    add_col = tabula_dfs[1]
    payer_add = tabula_dfs[1]
    payer_address = process_tabula_address(payer_add)
    payer_address_details = extract_address_details(payer_address)
    other_info = other_details(file_path)

    master_dict = {
        "Payer": payer_address_details.get("Item", ""),
        "PayerName": 'Guardian',
        "PayerAddress": payer_address_details.get("AddressElements", ""),
        "PayerCity": payer_address_details.get("PlaceName", ""),
        "PayerState": payer_address_details.get("StateName", ""),
        "PayerZip": payer_address_details.get("ZipCode", ""),
        "Payee": payee_address_details.get("Item", ""),
        "PayeeName": payee_address_details.get("ItemName", ""),
        "PayeeAddress": payee_address_details.get("AddressElements", ""),
        "PayeeCity": payee_address_details.get("PlaceName", ""),
        "PayeeState": payee_address_details.get("StateName", ""),
        "PayeeZip": payee_address_details.get("ZipCode", ""),
    }
    master_dict = {**master_dict, **other_info}
    return master_dict


def get_master_details(file_path, texts, url):
    with pdfplumber.open(file_path) as pdf:
        patients = []
        for page in pdf.pages:
            tables = page.extract_tables()
            t = 1
            for table in tables:

                t += 1
                r = 1
                for row in table[:-1]:
                    r += 1
                    if 'Claim Number' in row[0]:
                        patient_dict = {}
                        text = row[0]
                        claimnumber = text.split('Claim Number: ')[1].split(' ')[0]
                        patientaccountno = text.split('Patient Account No.:')[1].split(' ')[0]
                        plannumber = text.split('Plan Number:')[1].split(' ')[0].split('\n')[0]
                        patientname = text.split('Patient Name: ')[1].split('Employee Name')[0].strip()
                        employeename = text.split('Employee Name: ')[1].split('Relationship')[0].strip()
                        relationship = text.split('Relationship: ')[1].split('Planholder:')[0].replace('\n', '')
                        planholder = text.split('Planholder: ')[1]

                        patient_dict['SubscriberID'] = ''
                        patient_dict['PatientName'] = patientname
                        patient_dict['Relationship'] = relationship
                        patient_dict['ClaimId'] = claimnumber
                        patient_dict['PatientAccount'] = patientaccountno
                        patient_dict['PlanNumber'] = plannumber
                        patient_dict['SubscriberName'] = employeename
                        patient_dict['PlanType'] = planholder
                        patient_dict['TransactionFee'] = '$0.00'
                        patient_dict['url'] = url
                        patient_dict['PayerClaimID'] = ''
                        patient_dict['TotalAmount'] = ''
                        patient_dict['ClaimStatus'] = 'Processed'
                        patient_dict['RenderingProvider'] = ''
                        payee_address_details = get_basic_details(file_path)
                        notes = getRemarks(texts, claimnumber)
                        patient_dict.update(payee_address_details)
                        patient_dict['PayerClaimID'] = claimnumber
                        patient_dict['Notes'] = notes
                        benefit, adjustments = getBenefit(texts, claimnumber)
                        patient_dict.update(benefit)

                        patient_dict['PPGridViewId'] = 6
                        patient_dict['PPTransPayorListID'] = "27e7c674-051c-40ec-b9ef-6c84f3a3dd1d"
                        patient_dict['PayeeTaxID'] = ''
                        patient_dict['PayerContact'] = '(800) 541-7846'
                        patient_dict['PayerID'] = ''
                        patient_dict['PaymentMethodCode'] = ''
                        patient_dict['RecordID'] = str(uuid.uuid4())
                        patient_dict['RenderingProviderID'] = ''

                        patients.append((patient_dict))

    pl = len(patients)
    indexlist = []
    for i in range(pl):
        try:
            for j in range(i + 1, pl + 1):
                try:
                    if patients[i]["ClaimId"] == patients[j]["ClaimId"]:
                        indexlist.append(j)
                except:
                    pass
        except:
            pass

    indexlist.sort(reverse=True)

    for index in indexlist:
        del patients[index]

    return patients


def benfi(texts, a):
    pass


def get_details(file_path, texts, eobclaimmaster):
    dict_list = tabula.read_pdf(file_path, pages='all')

    lst = []
    for ind, tab in enumerate(dict_list):
        print("TAb", tab)
        if any('Claim Number' in col for col in tab.columns):
            new_columns_name = {}
            for i in range(len(tab.columns)):
                a = {}
                old_name = tab.columns[i]
                new_name = f'columns{i + 1}'
                new_columns_name[old_name] = new_name
                tab = tab.rename(columns=new_columns_name)

            lst.append(tab.to_dict('records'))

    temp_lst = []
    for i in range(len(lst)):
        for obj in lst[i]:
            if type(obj.get('columns1')) != float:
                temp_lst.append(obj)

    filtered_lst = []
    for i in range(len(temp_lst)):
        t = str(temp_lst[i]['columns2'])
        temp_lst[i]['columns2'] = t
        if not temp_lst[i]['columns1'].startswith('Patient Name') and not temp_lst[i]['columns1'].startswith(
                'Planholder') and not temp_lst[i]['columns1'].startswith('Line Submitted') and not temp_lst[i][
            'columns1'].startswith('No.'):
            filtered_lst.append(temp_lst[i])
    print("filtered_lst>>>>>>>>>>>>>>>>>", filtered_lst)

    new_lst = []
    new_dict = {}
    for obj in filtered_lst:
        columns3 = obj['columns3'].split()
        print(columns3)
        columns4 = obj['columns4'].split()

        if 'columns6' in obj:
            columns6 = str(obj['columns6']).split()
            columns4 = obj['columns4'].split()
            if len(columns6) == 3 and len(columns4) == 3:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': obj["columns2"],
                    'ToothNo': obj["columns3"],
                    'DateOfService': columns4[0],
                    'SubmittedCharge': columns4[1],
                    'ConsideredCharge': columns4[2],
                    'CoveredCharge': obj["columns5"],
                    'DeductibleAmount': columns6[0],
                    'CoveragePercent': columns6[1],
                    'BenefitAmount': columns6[2]
                }
            elif len(columns6) == 2 and len(columns4) == 3:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': obj["columns2"],
                    'ToothNo': obj["columns3"],
                    'DateOfService': columns4[0],
                    'SubmittedCharge': columns4[1],
                    'ConsideredCharge': columns4[2],
                    'CoveredCharge': obj["columns5"],
                    'DeductibleAmount': "",
                    'CoveragePercent': columns6[0],
                    'BenefitAmount': columns6[1]
                }
            elif len(columns6) == 1 and len(columns4) == 4:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': obj["columns2"],
                    'ToothNo': obj["columns3"],
                    'DateOfService': columns4[0],
                    'SubmittedCharge': columns4[1],
                    'ConsideredCharge': columns4[2],
                    'CoveredCharge': columns4[3],
                    'DeductibleAmount': "",
                    'CoveragePercent': obj["columns5"],
                    'BenefitAmount': str(obj["columns6"])
                }
        elif len(columns3) == 3:
            columns2 = obj['columns2'].split()
            columns4 = obj['columns4'].split()
            new_dict = {
                'SubmittedADACodesDescription': obj["columns1"],
                'AltCode': "",
                'ToothNo': columns2[0],
                'DateOfService': columns2[1],
                'SubmittedCharge': columns3[0],
                'ConsideredCharge': columns3[1],
                'CoveredCharge': columns3[2],
                'DeductibleAmount': "",
                'CoveragePercent': columns4[0],
                'BenefitAmount': str(columns4[1])
            }
        elif len(obj) == 5:
            columns5 = obj['columns5'].split()
            columns2 = ""
            if obj['columns2'].startswith('nan'):
                obj['columns2'] = ""
            else:
                columns2 = obj['columns2'].split()

            columns4 = obj['columns4'].split()
            if len(columns3) == 1:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': "",
                    'ToothNo': obj['columns3'],
                    'DateOfService': columns4[0],
                    'SubmittedCharge': columns4[1],
                    'ConsideredCharge': columns4[2],
                    'CoveredCharge': columns4[3],
                    'DeductibleAmount': "",
                    'CoveragePercent': columns5[0],
                    'BenefitAmount': str(columns5[1])
                }
                print("new_dict>>>>>>>>>>>>>>>", new_dict)

            elif len(columns5) == 2:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': "",
                    'ToothNo': obj['columns2'],
                    'DateOfService': columns3[0],
                    'SubmittedCharge': columns3[1],
                    'ConsideredCharge': columns3[2],
                    'CoveredCharge': columns3[3],
                    'DeductibleAmount': "",
                    'CoveragePercent': columns4[0],
                    'BenefitAmount': str(columns4[1])
                }
                print("new_dict>>>>>>>>>>>>>>>", new_dict)

            elif len(columns5) == 3:
                new_dict = {
                    'SubmittedADACodesDescription': obj["columns1"],
                    'AltCode': "",
                    'ToothNo': columns2[0],
                    'DateOfService': columns2[1],
                    'SubmittedCharge': columns3[0],
                    'ConsideredCharge': columns3[1],
                    'CoveredCharge': obj["columns4"],
                    'DeductibleAmount': columns5[0],
                    'CoveragePercent': columns5[1],
                    'BenefitAmount': str(columns5[2])
                }
                print("new_dict>>>>>>>>>>>>>>>", new_dict)


        else:
            columns3 = obj['columns3'].split()
            columns4 = obj['columns4'].split()
            new_dict = {
                'SubmittedADACodesDescription': obj["columns1"],
                'AltCode': "",
                'ToothNo': obj["columns2"],
                'DateOfService': columns3[0],
                'SubmittedCharge': columns3[1],
                'ConsideredCharge': columns3[2],
                'CoveredCharge': columns3[3],
                'DeductibleAmount': "",
                'CoveragePercent': columns4[0],
                'BenefitAmount': columns4[1]
            }

        if str(new_dict['AltCode']) == 'nan':
            new_dict['AltCode'] = str(new_dict['AltCode']).replace('nan', '')
        if str(new_dict['ToothNo']) == 'nan':
            new_dict['ToothNo'] = str(new_dict['ToothNo']).replace('nan', '')

        change_keys = [("DateOfService", "ServiceDate"), ("SubmittedCharge", "SubmittedCharges"),
                       ("BenefitAmount", "PayableAmount"), ("ConsideredCharge", "ActualAllowed"),
                       ("DeductibleAmount", "ContractualObligations")]
        for k in change_keys:
            old_key = k[0]
            new_key = k[1]
            value = new_dict[old_key]
            new_dict[new_key] = value
            del new_dict[old_key]
        proccode = new_dict['SubmittedADACodesDescription'].split(' ')[1].split('/')[0]
        description = new_dict['SubmittedADACodesDescription'].split('/')[-1]
        del new_dict['SubmittedADACodesDescription']
        new_dict.update({'ProcCode': proccode, 'Description': description, 'PatientResp': '', 'Adjustments': '',
                         'OtherAdjustments': '',
                         'Enrollee_ClaimID': '', 'PPGridViewId': 6, 'RemarkCodes': '', 'PayerInitiatedReductions': '',
                         "EFT_CheckNumber": eobclaimmaster[0]['EFT_CheckNumber'],
                         "PPTransPayorListID": "27e7c674-051c-40ec-b9ef-6c84f3a3dd1d", "RecordID": str(uuid.uuid4())})
        print("AAAAAAA", new_dict)

        new_lst.append(new_dict)
    print("new_lst>>>>>>>>>>>>>", new_lst)

    return new_lst


def getEftPatients(eobclaimmaster):
    eftpatientlist = []
    for p in eobclaimmaster:
        eftpatient_dict = {
            "SubscriberID": "",
            "ProviderClaimId": '',
            "PayerClaimId": p['ClaimId'],
            "MemberNo": p['PatientAccount'],
            "RenderingProviderFirstName": p['Provider'].split(' ')[0].strip(),
            "RenderingProviderLastName": p['Provider'].split(' ')[-1].strip(),
            "PatientName": p['PatientName'],
            "PatientFirstName": p['PatientName'].split(' ')[0].strip(),
            "PatientLastName": p['PatientName'].split(' ')[-1].strip(),
            "PlanType": p['PlanType'],
            "PlanNumber": p['PlanNumber'],
            "RenderingProviderID": "",
            "PayerPaid": p['TotalAmount'],
            "RecordID": str(uuid.uuid4()),
            "PPTransPayorListID": "27e7c674-051c-40ec-b9ef-6c84f3a3dd1d",
            "ClientId": "",
            "EligibilityVerificationId": "44",
            "EFT_CheckNumber": p['EFT_CheckNumber']
        }
        eftpatientlist.append(eftpatient_dict)
    return eftpatientlist


def filedownload_(url):
    """
    To download pdf from blob url
    Args:
        url:
    Returns:
        filepath of pdf
    """
    file_path = (
            "".join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".pdf"
    )
    print(file_path)
    input_file = url.replace("%20", " ")
    print("input_file>>>>>>>>>>>>>>", input_file)
    Downloader("Payment Processing", file_path, input_file)

    return file_path


def main():
    # url = data["EFTPatients"][0]["url"]

    url = "https://sdppcontainerdevsa.blob.core.windows.net/pp-scrapper-ins-blob/Payment%20Processing/Guardian/8EMBI63TTJ/8a7f3sd254221edssd/main.pdf"

    print("main 1")
    file_path = 'C:\\guardian\\SD%20Payor%20Scraping\\guardian.pdf'
    # file_path = filedownload_(url.replace("%20", " "))
    texts = getAllTexts(file_path)
    eobclaimmaster = get_master_details(file_path, texts, url)
    eobclaimdetail = get_details(file_path, texts, eobclaimmaster)
    eftpatients = getEftPatients(eobclaimmaster)

    json_data = {
        'EFTPatients': eftpatients,
        'PpEobClaimMaster': eobclaimmaster,
        'PpEobClaimDetail': eobclaimdetail
    }

    for i, (claim1, claim2, claim3) in enumerate(zip(
            json_data["EFTPatients"],
            json_data["PpEobClaimMaster"],
            json_data["PpEobClaimDetail"]
    ),
            start=1, ):
        claim1["RecordId"] = i
        claim2["RecordId"] = i
        claim3["RecordId"] = i

    return json_data


with open("wguardian_output.json", "r") as jsonFile:
    data = json.load(jsonFile)

data = main()

with open('guardian_output.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(data, indent=4))