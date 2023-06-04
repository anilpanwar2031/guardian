import tabula
from tabula import read_pdf
from tabulate import tabulate
from pypdf import PdfReader
import pdfplumber
import tika
from tika import parser
import pypdfium2 as pdfium
tika.initVM()
import sys
import json
import logging
import re
import zipfile
from pprint import pprint

from Utilities.pdf_utils import *
from FileDownload import Downloader


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


def getData(file_path):
    zipfile = extract_pdf_and_zip(file_path)
    df_list , json_data = zip_processor(zipfile)
    work_dict = json_getter(json_data)
    return df_list, work_dict


def change_header(dfs_list):
    d_list = []
    word = 'SERVICE'
    for df in dfs_list:
        cols = list(df.columns)
        for c in cols[0:1]:
            if word in c:
                break
            else:
                header_row_index = 0
                header_row = df.iloc[header_row_index]
                df = df.set_axis(header_row, axis='columns')
                df.drop(index=header_row_index,inplace=True)
                break
        d_list.append(df)
    return d_list   


def change_header_name(dfs_ch_list):
    dfs1 = []
    for d in dfs_ch_list:
        columns_list = d.columns.tolist()
        for i, c in enumerate(columns_list):
            if 'SERVICE DATES' in c:
                columns_list[i] = 'ServiceDate'
            if 'SERVICE CODE' in c:
                columns_list[i] = 'ProcCode'
            if 'ALTERNATE BENEFIT' in c:
                columns_list[i] = 'AlternateBenefitCode'
            if 'TOOTH' in c:
                columns_list[i] = 'ToothNumber'
            if 'SURFACE' in c:
                columns_list[i] = 'Surface'
            if 'SUBMITTED CHARGES' in c:
                columns_list[i] = 'SubmittedCharges'
            if 'ALLOWABLE AMOUNT' in c:
                columns_list[i] = 'Allowableamount/QPA'
            if 'COPAY AMOUNT' in c:
                columns_list[i] = 'CopayAmount'
            if 'NOT SEE PAYABLE REMARKS' in c:
                columns_list[i] = 'ContractualObligations' 
            if 'DEDUCTIBLE' in c:
                columns_list[i] = 'Deductible'  
            if 'CO INSURANCE' in c:
                columns_list[i] = 'CoInsurance'
            if 'PATIENT RESP' in c:
                columns_list[i] = 'PatientResp'
            if 'PAYABLE AMOUNT' in c:
                columns_list[i] = 'PayableAmount'
            if 'NUM. SVCS' in c:
                columns_list[i] = 'RemarkCodes'
            if 'NOT PAYABLE' in c:
                columns_list[i] = 'NotPayable'
            if 'SEE REMARKS' in c:
                columns_list[i] = 'SeeRemarks'     
                               
        d.columns = columns_list
        dfs1.append(d)

    t_list = []

    for df in dfs1:
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.fillna('')
        # if 'NumSVCS' in df.columns:
        #     df.rename(columns={'NumSVCS': 'RemarkCodes'}, inplace=True)
        #     df.drop('SurfaceNumSvcs', axis=1, inplace=True)
        # else:
        #     df.rename(columns={'SurfaceNumSvcs': 'RemarkCodes'}, inplace=True)
            
        t_list.append(df)

    dt = []
    for df in t_list:
        for i in range(df.shape[0] - 1):
            if df.iloc[i, 0] == '':
                col_index = df.columns.get_loc('ContractualObligations')
                df.iloc[i - 1, col_index] = df.iloc[i - 1, col_index] + ' ' + df.iloc[i, col_index]
                df = df.drop(i).reset_index(drop=True)
                i = 0
        dt.append(df)

    t_data_dict = []
    count = 1
    print("DTTTT")
    for t in dt:
        t = t.to_dict("records")
        for i in t:
            i.update({'ActualAllowed':'', 'Enrollee_ClaimID':'', 'OtherAdjustments':'', 'PayerInitiatedReductions':'', 'Adjustments':''})
        t_data_dict.append(t)

    return t_data_dict    


def get_basic_details(filepath):
    tabula_dfs = tabula.read_pdf(filepath,guess=False,pages=1,stream=True,encoding="utf-8",
        area =[(18, 26, 81, 233), (33,363,172,543), (128,26,193,265)],multiple_tables=True)
                 # y1,x1,y2,x2
    add_col = tabula_dfs[0].columns[0]
    payer_add = f"aetna {add_col} {' '.join(tabula_dfs[0][add_col ].to_list())}"
    
    payer_address_details = extract_address_details(payer_add)

    payment_col = tabula_dfs[2].columns[0]
    payment_add = f"{payment_col} {' '.join(tabula_dfs[2][payment_col ].to_list())}"
    payee_address_details = extract_address_details(payment_add)

    other_det_col = tabula_dfs[1].columns[0]
    other_det_list = tabula_dfs[1][other_det_col ].to_list()

    for item in other_det_list:
        if 'Trace Number:' in item:
            trace_num = item.split('Trace Number:')[1].strip()

        if 'Trace Amount:' in item:
            trace_amount = item.split('Trace Amount:')[1].strip()
            
    master_dict = {
        "Payer": payer_address_details.get("Item", ""),
        "PayerName": 'aetna',
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
        "EFT_CheckNumber": trace_num
    }
    return master_dict, trace_num


def extract_notes(text:str, provider_name:str)-> str:
    remark = ''
    if 'Remarks' in text:
        remark = text.split('\nRemarks:')[1]
        if 'For questions regarding this claim or if you wish a review of this decision:' in remark:
            remark = remark.split('For questions regarding this claim or if you wish a review of this decision:')[0]
        if provider_name in remark:
            remark = remark.split(provider_name)[0]
    return remark.replace("\n", "").strip()


def providerList(tables):
    providers_df = tables[0]
    providers_list = []
    for i in range(providers_df.shape[0] - 1):
        provider_dict = {}
        provider_dict['Name'] = providers_df.iloc[i, 0]
        provider_dict['Pin'] = providers_df.iloc[i, 1]
        provider_dict['Amount'] = providers_df.iloc[i, 3]
        providers_list.append(provider_dict)

    return providers_list


def get_master_details(texts, file_path, url, tables, totalamount, eftsettlementdate):
    providers_list = providerList(tables)
    all_patients = []
    provider_ele = texts.split('Total Payment to:')
    for x in range(len(provider_ele[:-1])):
        PATIENT=provider_ele[x].split('Patient Name:')
        
        for j in range(len(PATIENT)):

            for i in PATIENT[j].split('Claim ID:')[1:]:
                
                patient_dict = {}
                patient_name = PATIENT[j].split('Claim ID')[0].split('\n')[0].strip()
                patient_name, relation = patient_name.split('(')
                patient_dict['PatientName'] = patient_name.strip()
                patient_dict['Relationship'] = relation.replace(')', '').strip()
                patient_dict['ClaimId'] = i.split(' ')[1].strip()
                patient_dict['Recd'] = i.split('Recd:')[1].split(' ')[1].strip()
                patient_dict['MemberID'] = i.split('Member ID:')[1].split(' ')[1].strip()
                patient_dict['PatientAccount'] = i.split('Patient Account:')[1].split(' ')[1].strip()
                patient_dict['Member'] = i.split('Member:')[1].split('\n')[0].strip()
                patient_dict['GroupName'] = i.split('Group Name:')[1].split('Group Number')[0].split('\n')[0].strip()
                patient_dict['GroupNumber'] = i.split('Group Number:')[1].split('Product')[0].split('\n')[0].strip()
                patient_dict['Product'] = i.split('Product:')[1].split('Network ID:')[0].split('\n')[0].strip()
                patient_dict['NetworkID'] = i.split('Network ID:')[1].strip().split(' ')[0].strip()
                provider_name = provider_ele[x+1].split('\n')[0].strip().split('$')[0]
                patient_dict['Provider'] = provider_name.strip()
                patient_dict['TransactionFee'] = '$0.00'
                patient_dict['url'] = url
            
                patient_dict['Notes'] = extract_notes(i, provider_name)
                my_dict, eftnumber = get_basic_details(file_path)
                patient_dict = {**patient_dict, **my_dict}

                patient_dict['PayerClaimID'] = i.split(' ')[1].strip()
                patient_dict['TotalAmount'] = totalamount
                patient_dict['ClaimStatus'] = ''
                patient_dict['RenderingProvider'] = provider_name.strip()


                for p in providers_list[:-1]:
                    total_amount = providers_list[-1]['Amount']
                    if p['Name'] in str(patient_dict['Provider']):
                        patient_dict['RenderingProviderID'] = p['Pin']
                        patient_dict['PayerPaid'] = total_amount

                patient_dict['PaymentMethodCode'] = ''
                patient_dict['PayerContact'] = ''
                patient_dict['PayerID'] = ''
                patient_dict['PayeeTaxID'] = ''
                patient_dict['EFT_CheckDate'] = eftsettlementdate
                patient_dict['TotalPatientResp'] = ''

                all_patients.append(patient_dict)

    return all_patients, eftnumber            


def eobpatients(eobclaimmaster,tables):

    providers_list = providerList(tables)

    eobpatient_list = []
    for e in eobclaimmaster:
        eobpatient_dict = {}
        pfname, plname = e['PatientName'].split(' ')[0], e['PatientName'].split(' ')[-1]
        eobpatient_dict['ProviderClaimId'] = ''
        eobpatient_dict['PatientFullName'] = e['PatientName']
        eobpatient_dict['PayerClaimId'] = e['ClaimId']
        eobpatient_dict['MemberNo'] = e['MemberID']
        eobpatient_dict['SubscriberID'] = ''
        eobpatient_dict['RenderingProviderFirstName'] = e['Provider'].split(' ', 1)[0].strip()
        eobpatient_dict['RenderingProviderLastName'] = e['Provider'].split(' ', 1)[1].strip()
        eobpatient_dict['PatientName'] = e['PatientName']
        eobpatient_dict['ServiceDate'] = ''
        eobpatient_dict['EFT_CheckNumber'] = e['EFT_CheckNumber']
        eobpatient_dict['PatientFirstName'] = pfname
        eobpatient_dict['PatientLastName'] = plname
        eobpatient_dict['Enrollee_ClaimID'] = ''
        eobpatient_dict['OtherAdjustments'] = ''
        eobpatient_dict['PlanType'] = ''

        for p in providers_list[:-1]:
            total_amount = providers_list[-1]['Amount']
            if p['Name'] in str(e['Provider']):
                eobpatient_dict['RenderingProviderID'] = p['Pin']
                eobpatient_dict['PayerPaid'] = total_amount

        eobpatient_list.append(eobpatient_dict)
    return eobpatient_list


def main(data):
    print("main 1")
    url = data["PpEobClaimMaster"][0]["url"].replace("%20", " ")
    tinpin = data["PpEobClaimMaster"][0]["tinpin"]
    paidprovdername = data["PpEobClaimMaster"][0]["PaidProviderName"]
    providerid = data["PpEobClaimMaster"][0]["ProviderID"]
    eobdate = data["PpEobClaimMaster"][0]["EobDate"]
    eftsettlementdate = data["PpEobClaimMaster"][0]["EftSettlementDate"]
    totalamount = data["PpEobClaimMaster"][0]["TotalAmount"]

    file_path = filedownload_(url)
    dfs, work_d = getData(file_path)
    tables = tabula.read_pdf(file_path, pages='all')

    texts = []
    for t in work_d['elements']:
        texts.append(t['Text'])
    texts = '\n'.join([t['Text'] for t in work_d['elements']])    

    dfs_list = [d for d in dfs if d.shape[1] >= 10]
    dfs_ch_list = change_header(dfs_list)
    table_data_dict = change_header_name(dfs_ch_list)
    
    eobclaimmaster, eftnumber = get_master_details(texts, file_path, url, tables, totalamount, eftsettlementdate)
 
    eobclaimdetail = process_list(table_data_dict)
    for item in eobclaimdetail:
        item.update({'EFT_CheckNumber': eftnumber})

    eob_patients = eobpatients(eobclaimmaster, tables)

    json_data = {
        'EFTPatients': eob_patients,
        'PpEobClaimMaster': eobclaimmaster,
        'PpEobClaimDetail': eobclaimdetail
    }

    for i, (claim1, claim2, claim3) in enumerate(zip(
                json_data["EFTPatients"],
                json_data["PpEobClaimMaster"],
                json_data["PpEobClaimDetail"],
            ),
            start=1,):
        claim1["RecordID"] = i
        claim2["RecordID"] = i
        claim3["RecordID"] = i

    return json_data


# data = main()


# with open('aetna_output.json', 'w', encoding='utf-8') as file:
#     file.write(json.dumps(data, indent=4))
# pprint(data)