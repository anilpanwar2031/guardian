import tabula
from tabula import read_pdf
from tabulate import tabulate
from pypdf import PdfReader
import pdfplumber
import tika
from tika import parser
import pypdfium2 as pdfium
#
tika.initVM()
import sys
import json
import logging
import re
import zipfile
from pprint import pprint

from Utilities.pdf_utils import *
from FileDownload import Downloader

import tabula
import pandas as pd


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
                                     area= (96, 287, 153, 572), multiple_tables=True)
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
                                 area=[(141, 43, 176, 217), (25, 90, 53, 213), (97, 288, 152, 570)], multiple_tables=True)
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


def get_master_details(file_path):
    with pdfplumber.open(file_path) as pdf:
        patients = []
        for page in pdf.pages:
            tables = page.extract_tables()
            t = 1
            for table in tables:
                print("\n")
                t += 1
                r = 1
                for row in table[:-1]:
                    r += 1
                    if 'Claim Number' in row[0]:
                        patient_dict = {}
                        text = row[0]
                        claimnumber = text.split('Claim Number: ')[1].split(' ')[0]
                        patientaccountno = text.split('Patient Account No.:')[1].split(' ')[0]
                        plannumber = text.split('Plan Number:')[1].split(' ')[0]
                        patientname = text.split('Patient Name: ')[1].split('Employee Name')[0]
                        employeename = text.split('Employee Name: ')[1].split('Relationship')[0]
                        relationship = text.split('Relationship: ')[1].split('Planholder:')[0].replace('\n', '')
                        planholder = text.split('Planholder: ')[1]

                        patient_dict['SubscriberID'] = ''
                        patient_dict['PatientName'] = patientname
                        patient_dict['Relationship'] = relationship
                        patient_dict['ClaimId'] = claimnumber
                        patient_dict['PatientAccount'] = patientaccountno
                        patient_dict['TransactionFee'] = ''
                        patient_dict['url'] = ''
                        patient_dict['Notes'] = ''
                        patient_dict['PayerClaimID'] = ''
                        patient_dict['TotalAmount'] = ''
                        patient_dict['ClaimStatus'] = ''
                        patient_dict['RenderingProvider'] = ''
                        payee_address_details = get_basic_details(file_path)
                        patient_dict.update(payee_address_details)
                        patient_dict['PayerClaimID'] = claimnumber
                        patients.append((patient_dict))

    return patients


def main():
    print("main 1")
    file_path = 'C:\\guardian\\SD%20Payor%20Scraping\\guardian11.pdf'
    claimamster = get_master_details(file_path)

    return claimamster


data = main()


with open('guardian_output.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(data, indent=4))
pprint(data)