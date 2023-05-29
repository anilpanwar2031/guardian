import sys
import os
import json
import random
import string
import re
from nameparser import HumanName
from datetime import datetime
import pandas as pd
import tabula

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from Utilities.pdf_utils import  extract_payee_address,\
    get_data_in_format, extract_address_details, process_list
from FileDownload import Downloader


def filedownload_(url):

    file_path = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".pdf"
    print(file_path)
    input_file = url.replace("%20", " ")
    print("input_file>>>>>>>>>>>>>>", input_file)
    Downloader('Payment Processing', file_path, input_file)

    return file_path

def read_pdf_with_tabula(file_path: str, options: dict) -> tuple[list[dict], list[pd.DataFrame]]:
    """
    Extracts tables from PDF files using the Tabula package and returns a tuple of a list of
    dictionaries and a list of processed pandas DataFrames.

    Args:
        file_path (str): The path to the PDF file to extract tables from.
        options (dict): A dictionary of options to pass to the Tabula `read_pdf` function.

    Returns:
        A tuple containing a list of dictionaries, where each dictionary represents a table
        extracted from the PDF file, and a list of processed pandas DataFrames.
    """
    data_frames = tabula.read_pdf(file_path,
                                  **options, pages='all',
                                  pandas_options={'header': None})
    processed_dfs = []
    dicts = []

    for df in data_frames:
        if df.empty or len(df) <= 1:
            continue

        df.columns = ['DATE(S)\rOF SVC',
                      'NUM\rOF\rSVCS',
                      'PL\rOF\rSVC',
                      'PROCEDURE\rCODE/ TOOTH\rNUMBERS/',
                      'PROVIDER\rCHARGE',
                      'ALLOWANCE',
                      'NON-\rCHARGEABLE\rAMOUNT',
                      'NON-\rCHG\rCODE',
                      'SUBSCRIBER\rLIABILITY\rAMOUNT',
                      'SUB\rLIAB\rCODE',
                      'OTHER\rINSURANCE\rAMOUNT',
                      'AMOUNT(S)\rPAID TO\rPROVIDER',
                      'AMOUNT(S)\rPAID TO\rSUBSCRIBE',
                      'MESSAGE\rCODE(S)']

        for j, row in df.iterrows():
            if all([str(val).strip().replace(".", "").lower()
                    == str(col).strip().replace(".", "").lower()
                    for val, col in zip(row, df.columns)]):
                df.drop(j, inplace=True)

        df.columns = ['ServiceDate', 'NumOfServices', 'PlaceOfService',
                      'ProcCode', 'SubmittedCharges', 'ActualAllowed',
                      'ContractualObligations', 'Adjustments',
                      'SubscriberLiabilityAmount', 'SubscriberLiabilityCode',
                      'OtherInsuranceAmount', 'PayableAmount',
                      'PatientResp', 'RemarkCodes']

        try:
            df.fillna('', inplace=True)
            last_row = df.iloc[-1]
            prev_rows = df.iloc[:-1]
            df.reset_index(drop=True, inplace=True)

            if len(df) == 1 and pd.isna(df['ServiceDate'][0]):
                continue
            if len(df) == 1 and isinstance(df['ServiceDate'][0], str):
                try:
                    datetime.strptime(df['ServiceDate'][0], '%m/%d/%Y')
                except ValueError:
                    continue

            if not (last_row.astype(str).eq(prev_rows.iloc[0].astype(str))).all() and \
                    not (last_row.astype(str).eq(prev_rows.iloc[0].astype(str)).all()) \
                        and len(df) > 1:
                print()
                print('Last row values do not match the expected data types\
                      and formats of the previous rows')
                df.drop(df.tail(1).index, inplace=True)

        except Exception as e:
            print(f"An error occurred while processing DataFrame: {e}")

        processed_dfs.append(df)
        dicts.append(df.to_dict('records'))

    return dicts, processed_dfs

def get_payee_payor_details(data, work_dict):
    payor = data.get('EFTPatients')[0].get('Payor')
    payor_address_details = extract_address_details(payor + \
                                work_dict["elements"][0]['Text'] + work_dict["elements"][1]['Text'])
    payee_name, payee_search_string = extract_payee_address(work_dict)
    payee_address_details = extract_address_details(payee_search_string)

    for item in data.get('PpEobClaimMaster'):
        item.update ({
            'Payer': payor_address_details.get('Item', ''),
            'PayerName': payor,
            'PayerAddress': payor_address_details.get('AddressElements', ''),
            'PayerCity': payor_address_details.get('PlaceName', ''),
            'PayerState': payor_address_details.get('StateName', ''),
            'PayerZip': payor_address_details.get('ZipCode', ''),

            'Payee': payee_address_details.get('Item', ''),
            'PayeeName': payee_address_details.get('ItemName', ''),
            'PayeeAddress': payee_address_details.get('AddressElements', ''),
            'PayeeCity': payee_address_details.get('PlaceName', ''),
            'PayeeState': payee_address_details.get('StateName', ''),
            'PayeeZip': payee_address_details.get('ZipCode', ''),
        })

    return data


def extract_notes(work_dict, unique_adjustments, unique_liability_codes, unique_remark_codes):
    # Extract messages
    search_index1 = None
    search_index2 = None
    for i, key in enumerate(work_dict['elements']):
        text = key['Text']
        if 'MESSAGE(S):' in text:
            search_index1 = i
        elif any(code in text for code in unique_remark_codes):
            search_index2 = i

    if search_index1 is not None and search_index2 is not None:
        text_elements = work_dict['elements'][search_index1+1:search_index2+2]
        messages = ' '.join(elem['Text'] for elem in text_elements)
        codes = '|'.join(unique_adjustments | unique_liability_codes | unique_remark_codes)
        parts = re.split(fr'\b({codes})\b', messages)
        parts = [p.strip() for p in parts if p.strip()]
        messages = [a + ' ' + b for a, b in zip(parts[::2], parts[1::2])]

    else:
        messages = []

    # Extract liabilities
    search_index1 = None
    search_index2 = None
    for i, key in enumerate(work_dict['elements']):
        text = key['Text']
        if 'SUBSCRIBER LIABILITY CODES:' in text:
            search_index1 = i
        elif any(code in text for code in unique_liability_codes):
            search_index2 = i

    if search_index1 is not None and search_index2 is not None:
        text_elements = work_dict['elements'][search_index1+1:search_index2+1]
        liability_text = ' '.join(elem['Text'] for elem in text_elements)
        codes = '|'.join(unique_adjustments | unique_liability_codes | unique_remark_codes)
        parts = re.split(fr'\b({codes})\b', liability_text)
        parts = [p.strip() for p in parts if p.strip()]
        liabilities = [a + ' ' + b for a, b in zip(parts[::2], parts[1::2])]

    else:
        liabilities = []

    # Extract adjustments
    search_index1 = None
    search_index2 = None
    for i, key in enumerate(work_dict['elements']):
        text = key['Text']
        if 'NON-CHARGEABLE AMOUNT CODES:' in text:
            search_index1 = i
        elif any(code in text for code in unique_adjustments):
            search_index2 = i

    if search_index1 is not None and search_index2 is not None:
        text_elements = work_dict['elements'][search_index1+1:search_index2+2]
        adjustment_text = ' '.join(elem['Text'] for elem in text_elements)
        if 'SUBSCRIBER LIABILITY CODES:' in adjustment_text:
            adjustment_text = adjustment_text.replace('SUBSCRIBER LIABILITY CODES:', '')
        codes = '|'.join(unique_adjustments | unique_liability_codes | unique_remark_codes)
        parts = re.split(fr'\b({codes})\b', adjustment_text)
        parts = [p.strip() for p in parts if p.strip()]
        adjustments = [a + ' ' + b for a, b in zip(parts[::2], parts[1::2])]

    else:
        adjustments = []

    messages = [msg for msg in messages
                if not any(code in msg for code in (unique_adjustments | unique_liability_codes))]
    liabilities = [msg for msg in liabilities
                   if not any(code in msg for code in (unique_adjustments | unique_remark_codes))]
    adjustments = [msg for msg in adjustments if not
                   any(code in msg for code in (unique_liability_codes | unique_remark_codes))]

    msg_text = "MESSAGE(S):\n" + "\n".join(messages) if messages else ''
    liability_text = "SUBSCRIBER LIABILITY CODES:\n" "\n".join(liabilities) if liabilities else ''
    adjustment_text = "NON-CHARGEABLE AMOUNT CODES:\n" "\n".join(adjustments) if adjustments else ''
    
    text_blocks = [msg_text, liability_text, adjustment_text]
    notes = "\n".join(block for block in text_blocks if block)

    return notes


def extract_info(work_dict):
    results ={}

    for i, item in enumerate(work_dict.get('elements')):
        text = item.get('Text')

        # Extract provider name
        match = re.search(r'PROVIDER:\s*(.*?)\s*TIN', text)
        if match:
            provider_name = match.group(1)
            results['ProviderName'] = provider_name

        # Extract provider ID
        match = re.search(r'Provider ID:(\d+)', text)
        if match:
            provider_id = match.group(1)
            results['ProviderID'] = provider_id

        match = re.search(r'Appl/Sub Name:\s*(\S+)\s*(?:\S)?\s*(\S.*)', text, re.IGNORECASE)
        if match:
            results['SubscriberName'] = text.split(':')[-1].strip()

        match = re.search(r'EFT Number:\s*(\d+)\s*', text)
        match = re.search(r'ID Number:\s*(\d+)\s*', text)
        if match:
            id_number = match.group(1).strip()


    return results       


def main(data):
    url = data["EFTPatients"][0]["url"].replace('%20', ' ')

    eft_check_number = data["EFTPatients"][0]["DocumentID"]

    file_path = filedownload_(url)
    print(f'..........file path is..............\n {file_path}------------------------ ')

    _, work_dict = get_data_in_format(file_path)

    data = get_payee_payor_details(data, work_dict)

    results = extract_info(work_dict)

    # data = claim_master_data(data,work_dict,results)

    options = {"lattice": True, "guess": True, "encoding": "ISO-8859-1"}
    dicts, data_frames = read_pdf_with_tabula(file_path, options)

    data['PpEobClaimDetail'] = process_list(dicts)

    unique_adjustments = set()
    unique_liability_codes = set()
    unique_remark_codes = set()

    for df in data_frames:
        for col_name in ["Adjustments", "SubscriberLiabilityCode", "RemarkCodes"]:
            if col_name in df.columns:
                unique_values = {val for values in df[col_name].unique() for val in str(values).split("\r") if val != ''}
                if col_name == "Adjustments":
                    unique_adjustments.update(unique_values)
                elif col_name == "SubscriberLiabilityCode":
                    unique_liability_codes.update(unique_values)
                elif col_name == "RemarkCodes":
                    unique_remark_codes.update(unique_values)

    print("Unique Adjustments:", unique_adjustments)
    print("Unique Liability Codes:", unique_liability_codes)
    print("Unique Remark Codes:", unique_remark_codes)

    notes = extract_notes(work_dict, unique_adjustments, unique_liability_codes, unique_remark_codes)


    for item in data.get('PpEobClaimMaster'):

        patient = item.get('Patient')
        print(patient)
        for element in work_dict.get('elements'):
            text = element.get('Text')
            if text is None:
                continue
            text = text.split('ID Number:')[0] if 'ID Number:' in text else text
            match = re.search(r'Patient:\s*([A-Za-z]+\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s*(?:ID Number:\s*\d+)?', text, re.IGNORECASE)

            if not match:
                continue
            if 'ID Number:' in text:
                text = text.split('ID Number:')[0]

            patient_name = match.group(0).split(':')[-1].strip()
            print('text is ....', text)
            print('----------------patient name from pdf is', patient_name)

            if HumanName(patient_name.lower()).first == HumanName(patient.lower()).first and \
                    HumanName(patient_name.lower()).last == HumanName(patient.lower()).last:

                item.update({
                    'PatientName': patient_name,
                    'SubscriberName': results.get('SubscriberName', ''),
                    'EFT_CheckNumber': eft_check_number if eft_check_number else '',
                    'RenderingProviderID': results.get('ProviderID', ''),
                    'RenderingProvider': results.get('ProviderName', ''),
                    'PayerClaimID': item.pop('ClaimNo', ''),
                    'TotalAmount': item.pop('AmtPaid', ''),
                    'SubscriberID': item.pop('CertificateNo',''),
                    'Notes': notes,
                    'url': data["EFTPatients"][0]["url"],
                    'TransactionFee': '$0.00',
                    'PayerContact': '',
                    'PayeeTaxID': '',
                    'ClaimStatus': '',
                    'PaymentMethodCode': '',
                    'PayerID': '',
                    'ProviderClaimId': '',
                })
                item.pop('Patient')
                item.pop('Insured')

    patients = []
    for i,  patient in enumerate(data['PpEobClaimMaster']):
        patient_name_ = patient.get('PatientName', '')
        first_name = patient_name_.split(' ')[0] if patient_name_ else ''
        last_name = patient_name_.split(' ')[-1] if patient_name_ else ''

        patients.append({
            'ProviderClaimId': '',
            'PatientFullName': patient_name_,
            'PayerClaimId': patient.get('PayerClaimId', ''),
            'MemberNo': patient.get('PatientAccountNumber', ''),
            'PayerPaid': patient.get('TotalAmount', ''),
            'SubscriberID': patient.get('SubscriberID', ''),
            'RenderingProviderFirstName': '',
            'RenderingProviderLastName': '',
            'PatientName': patient.get('PatientName', ''),
            'ServiceDate': patient.get('ServiceDate', ''), 
            'RenderingProviderID': patient.get('RenderingProviderID', ''), 
            'EFT_CheckNumber': patient.get('EFT_CheckNumber', ''),
            'PatientFirstName' : first_name,
            'PatientLastName': last_name,
            'Enrollee_ClaimID': '',
            'OtherAdjustments': '',
            'PlanType': '',
            'RecordID': i
            })

    data['EFTPatients'] = patients

    for item in data.get('PpEobClaimDetail'):
        item.update({
            'Enrollee_ClaimID': '',
            'OtherAdjustments': '',
            'PayerInitiatedReductions': '',
            'EFT_CheckNumber': eft_check_number

        })

    for i, (claim1, claim2) in enumerate(zip(
        data["PpEobClaimMaster"],
        data["PpEobClaimDetail"],
    ), start=1):
        claim1["RecordID"] = i
        claim2["RecordID"] = i

    print(f'------------------------------ \n FINAL DATA IS \n {data}')
    return data

if __name__ == "__main__":
    # file_path = 'uc_hard.pdf'
    with open("output.json", "r") as f:
        data = json.load(f)
    data = main(data)
    with open("concordia_wraped.json", "w") as f:
        json.dump(data, f, indent=4)
