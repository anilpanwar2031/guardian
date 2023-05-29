import json
import re
import usaddress


def get_address(address_string, parsed_address):

    if parsed_address.get('PlaceName'):
        address_end_index = address_string.rfind(parsed_address['PlaceName'])
    elif parsed_address.get('StateName'):
        address_end_index = address_string.rfind(parsed_address['StateName'])
    elif parsed_address.get('ZipCode'):
        address_end_index = address_string.rfind(parsed_address['ZipCode'])
    elif parsed_address.get('CountryName'):
        address_end_index = address_string.rfind(parsed_address['CountryName'])
    else:
        address_end_index = len(address_string)

    address_string = address_string[len(parsed_address.get('Recipient', '')):address_end_index].strip()

    return address_string

def get_address_list_when_exception(parsed_address):

    address_list ={}
    name = ''
    for address_component in parsed_address:
        label = address_component[1]
        component = address_component[0]

        if label == 'StateName':
            address_list['StateName'] = component
        elif label == 'ZipCode':
            address_list['ZipCode'] = component
        elif label == 'PlaceName':
            address_list['PlaceName'] = component
        elif label == 'Recipient':
            name += f' {component}'
    address_list['Recipient'] = name

    return address_list


def second(json_data):
     
    pp_eob_claim_master = json_data.get('PpEobClaimMaster')
    for item in pp_eob_claim_master:

        payer = item.get('Payer')
        if payer is not None:
            try:
                address_list1 = usaddress.tag(payer)[0]
            except usaddress.RepeatedLabelError as e:
                parsed_address = e.parsed_string
                print('parsed address is for payor is----------', parsed_address )
                address_list1 = get_address_list_when_exception(parsed_address)

            item['PayerName'] = address_list1.get('Recipient', '')
            item['PayerAddress'] = get_address(payer, address_list1)

            item['PayerCity'] = address_list1.get('PlaceName', '')
            item['PayerState'] = address_list1.get('StateName', '')
            item['PayerZip'] = address_list1.get('ZipCode', '')

        item['PayerContact'] = item.pop('Contact')
        item['PayerID'] = item.pop('TransactionIDNumber')
        item['PaymentMethodCode'] = item.pop('PaymentMethod')

        Payee = item.get('Payee')
        if Payee is not None:
            try:
                address_list2 = usaddress.tag(Payee)[0]
            except usaddress.RepeatedLabelError as e:
                parsed_address = e.parsed_string
                address_list2 = get_address_list_when_exception(parsed_address)

            item['PayeeName'] = address_list2.get('Recipient', '')
            item['PayeeAddress'] = get_address(Payee, address_list2)

            item['PayeeCity'] = address_list2.get('PlaceName', '')
            item['PayeeState'] = address_list2.get('StateName', '')
            item['PayeeZip'] = address_list2.get('ZipCode', '')
        item['PayeeTaxID'] = item.pop('TIN_NPI')

        item['TransactionFee'] = '$0.00' if item.get('TransactionFee') == '' or item.get('TransactionFee') is None  else  item.get('TransactionFee')


        eft_check_number = item.get('EFT_CheckNumber')

        json_data["EFTPatients"] = [{**a, **{'PlanType':b['InsurancePlanType'],'RenderingProvider':b['RenderingProvider'],'PayerClaimNumber':b['PayerClaimID'],'RenderingProviderID':b['RenderingProviderID'],"ClaimStatus":b["ClaimStatus"], 'EFT_CheckNumber': b['EFT_CheckNumber']}} for a,b in zip(json_data.get("EFTPatients"), json_data.get("PpEobClaimMaster"))]

        print(f'------------------ json_data[EFTPatients] is \n{json_data["EFTPatients"]}\n------------------')
               

    for item in json_data.get('PpEobClaimDetail'):
        item['EFT_CheckNumber'] = eft_check_number if eft_check_number is not None else ''
        PatientResp = item.get('PatientResp') if item.get('PatientResp') is not None else item.get('PatientPays')

        print(PatientResp)
        item['PatientResp'] = PatientResp
        if PatientResp is not None:
            parts = PatientResp.split()
            item['Adjustments'] = parts[0] if len(parts) == 2 else ''
            item['PatientPays'] = parts[-1] if len(parts)>=1 else ''
    
    for item in json_data.get('EFTPatients'):
        patient_name = item.get('PatientName')
        RenderingProvider = item.get('RenderingProvider', None)
        item['RenderingProviderFirstName'] = RenderingProvider.split(' ')[0] if RenderingProvider is not None else ''
        item['RenderingProviderLastName'] = RenderingProvider.split(' ')[-1] if RenderingProvider is not None else ''
        item['PatientFirstName'] = patient_name.split(' ')[0]
        item['PatientLastName'] = patient_name.split(' ')[-1]

        
    for i, (claim1, claim2, claim3, claim4) in enumerate(zip(
        json_data["EFTPatients"],
        json_data["PpEobClaimMaster"],
        json_data["PpEobClaimDetail"],
        json_data["Status"]
    ), start=1):
        claim1["RecordID"] = i
        claim2["RecordID"] = i
        claim3["RecordID"] = i
        claim4["RecordID"] = i


    return json_data


def main(data):
    eft_details = data["EFTPatients"].pop(0)
    eft_details = eft_details["EFTDetails"]
    data["Status"] = eft_details

    claims = []

    for i, claim in enumerate(data["PpEobClaimMaster"]):
        if 'url' in claim.keys() and len(claim.keys()) <= 2:
            url = claim.pop('url')
            # Add this url to next dictionary
            data["PpEobClaimMaster"][i+1]["url"] = url

    for i, claim in enumerate(data["PpEobClaimMaster"]):
        if len(claim.keys()) == 1:
            # pop it from the list and append it to the claims list
            claims.append(data["PpEobClaimMaster"].pop(i))
    

    for d in data['PpEobClaimMaster']:
        print(d)
        d["TotalContractualObligations"] = d["TotalContractualObligations"].replace("(", "").replace(")", "")

    for d in data['EFTPatients']:
        if "Add'LAdjust" in d.keys():
            # Rename the key to Add'l Adjust
            d["Add'l Adjust"] = d.pop("Add'LAdjust")

    for d in data['EFTPatients']:
        claimid =     re.sub(r"\s+", "", d['PayerClaimId'])
        d['PayerClaimId']=claimid
        
        d['MemberNo']     =  re.sub(r"\s+", "", d['MemberNo'] )


    for claim in claims:
        for key, value in claim.items():
            for item_ in value:
                item_["Enrollee_ClaimID"] = key

    data["PpEobClaimDetail"] = []

    for claim in claims:
        for key, value in claim.items():
            for v in value:
                # if v["ServiceDate"] contains two '/'
                if v["ServiceDate"].count('/') == 2:
                    data["PpEobClaimDetail"].append(v)
    nums = '0123456789 '

    for i in range(len(data["EFTPatients"])):
        for key, value in data["EFTPatients"][i].items():
            try:
                # if value contains only numbers
                if all([j in nums for j in value]):
                    data["EFTPatients"][i][key] = data["EFTPatients"][i][key].replace(" ", "")
            except:
                pass        # If value is not an integer, do nothing

    #data["EFTPatient"] = data.pop("EFTPatients")

    data=second(data)

    print(f'\n..........final data is \n {data}')
    return data

if __name__ == "__main__":
    with open("output.json", "r") as f:
        data = json.load(f)
    data = main(data)
    with open("output_wrapped.json", "w") as f:
        json.dump(data, f, indent=4)