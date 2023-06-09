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
    # y1, x1, y2, x2
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


def remove_duplicate_dict(data_list):
    unique_dicts = list(set(map(lambda x: tuple(sorted(x.items())), data_list)))
    if len(unique_dicts) < len(data_list):
        return [dict(t) for t in unique_dicts]
    else:
        return data_list


def get_claimnumber(eobclaimmaster):
    claims = []
    for i in range(len(eobclaimmaster)):
        claims.append(eobclaimmaster[i]['ClaimId'])
    return claims


def get_details(file_path, texts, eobclaimmaster):
    dict_list = tabula.read_pdf(file_path, pages='all')

    lst = []

    claimlist = get_claimnumber(eobclaimmaster)
    print("Claim lsittttt", claimlist)
    for ind, tab in enumerate(dict_list):
        claimn = claimlist[ind]
        tab['Claim Number'] = claimn

        if any('Patient Name' in col for col in tab.columns):
            new_columns_name = {}
            for i in range(len(tab.columns)):
                old_name = tab.columns[i]
                new_name = f'columns{i + 1}'
                new_columns_name[old_name] = new_name

                tab = tab.rename(columns=new_columns_name)
            #         tabd = tab.to_dict('records')
            lst.append(tab.to_dict('records'))
        #     if len(lst) == 0:
        if any('Claim Number' in col for col in tab.columns):
            new_columns_name = {}
            for i in range(len(tab.columns)):
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
        if not temp_lst[i]['columns1'].startswith('Patient Name') and not temp_lst[i]['columns1'].startswith(
                'Planholder') and not temp_lst[i]['columns1'].startswith('Line Submitted') and not temp_lst[i][
            'columns1'].startswith('No.'):
            filtered_lst.append(temp_lst[i])
        if not temp_lst[i]['columns1'].startswith('Claim Number') and not temp_lst[i]['columns1'].startswith(
                'Planholder') and not temp_lst[i]['columns1'].startswith('Line Submitted') and not temp_lst[i][
            'columns1'].startswith('No.'):
            filtered_lst.append(temp_lst[i])

    updated_list = remove_duplicate_dict(filtered_lst)

    ls = updated_list
    for f in ls[:]:
        for k in f.keys():
            if 'Patient' in str(f[k]):
                ls.remove(f)

    print("filtered lsit", len(ls))

    new_lst = []
    for obj in ls:

        new_dict = {}

        columns2 = str(obj['columns2']).split()
        columns3 = obj['columns3'].split()
        columns4 = obj['columns4'].split()
        lastk = list(obj.keys())
        lastk = lastk[-1]
        new_dict.update({'Enrollee_ClaimID': obj[lastk]})
        keylist = list(obj.keys())[:-1]


        if 'columns7' in keylist:
            print("777777")
            columns7 = str(obj['columns7']).split()
            columns6 = obj['columns6'].split()
            columns5 = obj['columns5'].split()

            print("Lenght7", len(columns7))
            print("columns7", columns7)
            if len(columns7) == 3:
                new_dict.update(
                    {'DeductibleAmount': columns7[0], 'CoveragePercent': columns7[1], 'BenefitAmount': columns7[2]})
            if len(columns7) == 2:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns6[0], 'BenefitAmount': columns7[1]})
            if len(columns7) == 1:
                new_dict.update({'BenefitAmount': columns7[0]})

            print("Lenght6", len(columns6))
            print("columns6", columns6)
            if len(columns6) == 3:
                new_dict.update(
                    {'DeductibleAmount': columns6[0], 'CoveragePercent': columns6[1], 'BenefitAmount': columns6[2]})
            if len(columns6) == 2:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns6[0], 'BenefitAmount': columns6[1]})
            if len(columns6) == 1:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns6[0]})

            print("Lenght5", len(columns5))
            print("columns5", columns5)
            if len(columns5) == 3:
                new_dict.update(
                    {'SubmittedCharge': columns5[0], 'ConsideredCharge': columns5[1], 'CoveredCharge': columns5[2]})
            if len(columns5) == 2:
                new_dict.update({'ConsideredCharge': columns5[0], 'CoveredCharge': columns5[1]})
            if len(columns5) == 1:
                new_dict.update({'CoveredCharge': columns5[0]})

            print("Lenght4", len(columns4))
            print("columns4", columns4)
            if len(columns4) == 3:
                new_dict.update(
                    {'DateOfService': columns4[0], 'SubmittedCharge': columns4[1], 'ConsideredCharge': columns4[2]})
            if len(columns4) == 2:
                new_dict.update({'DateOfService': columns4[0], 'SubmittedCharge': columns4[1]})
            if len(columns4) == 1:
                new_dict.update({'DateOfService': columns4[0]})

            print("Lenght3", len(columns3))
            print("columns3", columns3)
            if len(columns3) == 1:
                new_dict.update({'ToothNo': columns3[0]})

            print("Lenght2", len(columns2))
            print("columns2", columns2)
            if len(columns2) == 1:
                new_dict.update({'AltCode': columns2[0]})
            new_dict.update({'SubmittedADACodesDescription': obj["columns1"]})



        elif 'columns6' in keylist:
            columns6 = obj['columns6'].split()
            columns5 = obj['columns5'].split()

            if len(columns6) == 3:
                new_dict.update(
                    {'DeductibleAmount': columns6[0], 'CoveragePercent': columns6[1], 'BenefitAmount': columns6[2]})
            if len(columns6) == 2:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns6[0], 'BenefitAmount': columns6[1]})

            if len(columns5) == 3:
                new_dict.update(
                    {'SubmittedCharge': columns5[0], 'ConsideredCharge': columns5[1], 'CoveredCharge': columns5[2]})
            if len(columns5) == 2:
                new_dict.update({'ConsideredCharge': columns5[0], 'CoveredCharge': columns5[1]})
            if len(columns5) == 1:
                new_dict.update({'CoveredCharge': columns5[0]})

            if len(columns4) == 3:
                new_dict.update(
                    {'DateOfService': columns4[0], 'SubmittedCharge': columns4[1], 'ConsideredCharge': columns4[2]})
            if len(columns4) == 2:
                new_dict.update({'DateOfService': columns4[0], 'SubmittedCharge': columns4[1]})
            if len(columns4) == 1:
                new_dict.update({'DateOfService': columns4[0]})

            if len(columns3) == 1:
                new_dict.update({'ToothNo': columns3[0]})

            if len(columns2) == 1:
                new_dict.update({'AltCode': ''})
            new_dict.update({'SubmittedADACodesDescription': obj["columns1"]})



        elif 'columns5' in keylist:

            print("555555")

            columns5 = obj['columns5'].split()

            if len(columns5) == 3:
                new_dict.update(
                    {'DeductibleAmount': columns5[0], 'CoveragePercent': columns5[1], 'BenefitAmount': columns5[2]})

            if len(columns5) == 2:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns5[0], 'BenefitAmount': columns5[1]})

            print("Length 4", len(columns4))

            print("value columns4", columns4)

            if len(columns4) == 4:
                new_dict.update(
                    {'DateOfService': columns4[0], 'SubmittedCharge': columns4[1], 'ConsideredCharge': columns4[2],
                     'CoveredCharge': columns4[3]})

                print("NEW DICT", new_dict)

            if len(columns4) == 3:
                new_dict.update(
                    {'SubmittedCharge': columns4[0], 'ConsideredCharge': columns4[1], 'CoveredCharge': columns4[2]})

            if len(columns4) == 2:
                new_dict.update({'ConsideredCharge': columns4[0], 'CoveredCharge': columns4[1]})

            if len(columns4) == 1:
                new_dict.update({'CoveredCharge': columns4[0]})

            print("Length 3", len(columns3))

            print("value columns3", columns3)

            if len(columns3) == 3:
                new_dict.update(
                    {'DateOfService': columns3[0], 'SubmittedCharge': columns3[1], 'ConsideredCharge': columns3[2]})

            if len(columns3) == 2:
                new_dict.update({'SubmittedCharge': columns3[0], 'ConsideredCharge': columns3[1]})

            if len(columns3) == 1:
                new_dict.update({'ToothNo': columns3[0]})

            print("Length 2 ", len(columns2))

            print("value columns2", columns2)

            if len(columns2) == 2:
                new_dict.update({'ToothNo': columns2[0], 'DateOfService': columns2[1]})

            if len(columns2) == 1:

                if columns2[0] == 'nan':

                    pass

                else:

                    new_dict.update({'ToothNo': columns2[0]})

            new_dict.update({'SubmittedADACodesDescription': obj["columns1"], 'AltCode': ""})



        elif 'columns4' in keylist:
            if len(columns4) == 3:
                new_dict.update(
                    {'DeductibleAmount': columns4[0], 'CoveragePercent': columns4[1], 'BenefitAmount': columns4[2]})
            if len(columns4) == 2:
                new_dict.update({'DeductibleAmount': '', 'CoveragePercent': columns4[0], 'BenefitAmount': columns4[1]})

            if len(columns3) == 4:
                new_dict.update(
                    {'DateOfService': columns3[0], 'SubmittedCharge': columns3[1], 'ConsideredCharge': columns3[2],
                     'CoveredCharge': columns3[3]})
            if len(columns3) == 3:
                new_dict.update(
                    {'SubmittedCharge': columns3[0], 'ConsideredCharge': columns3[1], 'CoveredCharge': columns3[2]})
            if len(columns3) == 2:
                new_dict.update({'ConsideredCharge': columns3[0], 'CoveredCharge': columns3[1]})
            if len(columns3) == 1:
                new_dict.update({'CoveredCharge': columns3[0]})

            if len(columns2) == 2:
                new_dict.update({'ToothNo': columns2[0], 'DateOfService': columns2[1]})
            if len(columns2) == 1:
                new_dict.update({'ToothNo': columns2[0]})

            new_dict.update({'SubmittedADACodesDescription': obj["columns1"], 'AltCode': ""})

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
                         'OtherAdjustments': '', 'RemarkCodes': '', 'PayerInitiatedReductions': '',
                         "EFT_CheckNumber": eobclaimmaster[0]['EFT_CheckNumber']
                         })

        new_lst.append(new_dict)

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

    Downloader("Payment Processing", file_path, input_file)

    return file_path


def main(data):
    url = data["EFTPatients"][0]["url"]

    print("main 1")
    # file_path = 'C:\\guardian\\SD%20Payor%20Scraping\\guardian.pdf'
    file_path = filedownload_(url.replace("%20", " "))
    texts = getAllTexts(file_path)
    eobclaimmaster = get_master_details(file_path, texts, url)
    eobclaimdetail = get_details(file_path, texts, eobclaimmaster)
    eftpatients = getEftPatients(eobclaimmaster)

    json_data = {
        'EFTPatients': eftpatients,
        'PpEobClaimMaster': eobclaimmaster,
        'PpEobClaimDetail': eobclaimdetail
    }

    return json_data

#     for i, (claim1, claim2, claim3) in enumerate(zip(
#             json_data["EFTPatients"],
#             json_data["PpEobClaimMaster"],
#             json_data["PpEobClaimDetail"]
#     ),
#             start=1, ):
#         claim1["RecordId"] = i
#         claim2["RecordId"] = i
#         claim3["RecordId"] = i
#
#     return json_data
#
#
# with open("wguardian_output.json", "r") as jsonFile:
#     data = json.load(jsonFile)
#
# data = main()
#
# with open('guardian_output.json', 'w', encoding='utf-8') as file:
#     file.write(json.dumps(data, indent=4))
