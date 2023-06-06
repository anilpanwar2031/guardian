import sys
import os
import uuid
#

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import json
from FileDownload import Downloader
import random, string
import tabula


def main(data):
    data['RcmEobClaimDetail'] = []
    # file_path = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".pdf"
    file_path = "guardian.pdf"
    print(file_path)
    # input_file = data["RcmEobClaimMaster"][0]["url"].replace("%20", " ")
    # print("input_file>>>>>>>>>>>>>>", input_file)
    # Downloader('Revenue Cycle Management', file_path, input_file)
    dict_list = tabula.read_pdf(file_path, pages='all')

    lst = []
    for ind, tab in enumerate(dict_list):
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
        new_lst.append(new_dict)
    print("new_lst>>>>>>>>>>>>>", new_lst)
    for i in new_lst:
        data['RcmEobClaimDetail'].append(i)

    ADACodes = ""
    Description = ""
    for i in range(len(data['RcmEobClaimDetail'])):
        for key, values in data['RcmEobClaimDetail'][i].items():
            if key == "SubmittedADACodesDescription":
                cdtcodes_type_of_service = values
                ADACodes, Description = cdtcodes_type_of_service.split("/", 1)
        data['RcmEobClaimDetail'][i]["ADACodes"] = ADACodes
        data['RcmEobClaimDetail'][i]["Description"] = Description
        del data['RcmEobClaimDetail'][i]["SubmittedADACodesDescription"]

    for obj in data['RcmEobClaimDetail']:
        ads_code = obj["ADACodes"].split()
        if len(ads_code) == 2:
            obj["ADACodes"] = ads_code[1]
    print("data>>>>>>>>>>>>>>", data)
    for obj in data["RcmEobClaimDetail"]:
        obj["RecordID"] = str(uuid.uuid4())

    if data.get("RcmEobClaimMaster"):
        for obj in data["RcmEobClaimMaster"]:
            obj["RecordID"] = str(uuid.uuid4())

    with open("newJson.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


with open("output.json", "r") as jsonFile:
    data = json.load(jsonFile)

main(data)