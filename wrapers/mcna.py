"""
Scrap data from pdf generated and provide structured data as output
"""

from typing import List, Dict, Tuple

import random
import string
import re
import pandas as pd
import tabula

import tika
from tika import parser

from Utilities.pdf_utils import extract_address_details, process_list
from FileDownload import Downloader


def process_dataframe(data_frame: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
    """
    Processes a pandas DataFrame containing dental insurance
    claim data and returns a list of dictionaries representing
    each claim.

    Args:
        data_frame: A pandas DataFrame containing dental insurance claim data.

    Returns:
        A list of dictionaries representing each claim in the DataFrame.
    """
    data_frame = data_frame.copy()
    data_frame.columns = [
        "Claim #",
        "Pat Ctrl #",
        "DOS",
        "T./A.",
        "Surf.",
        "CDT / Description",
        "Qty",
        "Billed",
        "Allowed",
        "Copay",
        "Exceeding BM",
        "Patient Resp.",
        "COB",
        "Interest",
        "Paid",
        "Denied",
        "Remarks",
    ]

    # use vectorized operations to remove rows that match column names
    data_frame = data_frame[
        ~data_frame.apply(
            lambda row: row.str.lower()
            .str.replace(".", "", regex=False)
            .str.strip()
            .eq(data_frame.columns.str.lower().str.replace(".", "", regex=False).str.strip())
            .all(),
            axis=1,
        )
    ]

    # fill null values with empty string
    data_frame.fillna("", inplace=True)

    data_frame.columns = [
        "Claim #",
        "MemberNo",
        "ServiceDate",
        "T./A.",
        "Surf.",
        "CDT / Description",
        "Qty",
        "SubmittedCharges",
        "ContractualObligations",
        "Copay",
        "Exceeding BM",
        "PatientResp",
        "COB",
        "Interest",
        "PayableAmount",
        "Denied",
        "RemarkCodes",
    ]

    # convert dataframe to list of dictionaries
    records = data_frame.to_dict("records")

    unique_ac_no = (
        data_frame.iloc[:-1]["MemberNo"].unique()[0]
        if len(data_frame.iloc[:-1]["MemberNo"].unique()) >= 1
        else ""
    )
    unique_service_date = (
        data_frame.iloc[:-1]["ServiceDate"].unique()[0]
        if len(data_frame.iloc[:-1]["ServiceDate"].unique()) >= 1
        else ""
    )
    unique_claim_no = (
        data_frame.iloc[:-1]["Claim #"].unique()[0]
        if len(data_frame.iloc[:-1]["Claim #"].unique()) >= 1
        else ""
    )

    # Combine into a dictionary
    result = [
        {
            "PatientAccountNumber": unique_ac_no,
            "ServiceDate": unique_service_date,
            "ProviderClaimId": unique_claim_no,
        }
    ]

    return records, result


def extract_totals(detail_list: List[Dict]) -> List[Dict]:
    """
    Extracts the total values from the claim details list.
    Args:
    detail_list (List[Dict]): A list of claim details where each detail
    is a dictionary with keys representing the columns and values
    representing the respective row values.

    Returns:
    List[Dict]: A list of dictionaries where each dictionary represents
    the total values for the respective claims.
    """

    # use generator expression to filter claim details
    tot_detail = (
        detail
        for detail in detail_list
        if "Total Subscriber" in detail.get("Claim #", "")
    )

    # use list comprehension to extract total values
    total_master = [
        {
            "TotalSubmittedCharges": detail.get("MemberNo", ""),
            "TotalContractualObligations": detail.get("ServiceDate", ""),
            "TotalCopay": detail.get("T./A.", ""),
            "TotalExceedingBM": detail.get("Surf.", ""),
            "TotalPatientResp": detail.get("CDT / Description", ""),
            "TotalCOB": detail.get("Qty", ""),
            "TotalInterest": detail.get("SubmittedCharges", ""),
            "TotalAmount": detail.get("ContractualObligations", ""),
            "TotalDenied": detail.get("Copay", ""),
        }
        for detail in tot_detail
    ]

    return total_master


def process_claim_details(df_list: List[pd.DataFrame]) -> List[Dict]:
    """
        Processes a list of pandas DataFrames containing dental
        insurance claim data and returns a list of dictionaries
        representing the processed claim details and total master
        details.

        Args:
            df_list (List[pd.DataFrame]): A list of pandas
            DataFrames containing dental insurance claim data.

        Returns:
            Tuple[List[Dict], List[Dict]]: A tuple containing the
            total master details and the processed claim details.
    """

    detail_list, detail = zip(*[process_dataframe(df) for df in df_list])
    claim_detail = process_list(detail_list)
    total_master = extract_totals(claim_detail)
    master_detail = process_list(list(detail))
    claim_detail = [
        detail
        for detail in claim_detail
        if "Total Subscriber" not in detail.get("Claim #")
    ]

    total_master = [{**a, **b} for a, b in zip(master_detail, total_master)]

    return total_master, claim_detail


def parse_patients_from_pdf(file_path: str) -> List[dict]:
    """
    Parses patient data from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        List[dict]: A list of dictionaries containing patient data.
    """
    tika.initVM()

    parsed_pdf = parser.from_file(file_path)
    pdf_content = parsed_pdf.get("content", "")

    if not pdf_content:
        print("ValueError('PDF file is empty.')")
        return []

    providers = pdf_content.split("Provider:")

    patients = []

    pattern = r"\n(\d+)/(\d+)\n"
    match = re.search(pattern, providers[0])
    payer_id, payee_tax = match.groups() if match else ("", "")

    plan = (
        providers[0].split("Plan:")[1].strip()
        if len(providers[0].split("Plan:")) > 1
        else ""
    )

    for provider in providers[1:]:
        provider_fields = provider.strip().split("\n")[0].split("/")
        if len(provider_fields) < 2:
            provider_name, provider_id = "", ""
        else:
            provider_name, provider_id = (
                provider_fields[1].strip(),
                provider_fields[0].strip(),
            )

        subscriber_list = provider.split("Subscriber ID/Name:")[1:]
        for subscriber in subscriber_list:
            subscriber_fields = subscriber.split(" DOB:")
            patient = {
                "InsurancePlanType": plan,
                "RenderingProvider": provider_name,
                "RenderingProviderID": provider_id,
                "SubscriberID": subscriber_fields[0].split("/")[0].strip()
                if "/" in subscriber_fields[0]
                else "",
                "PatientName": subscriber_fields[0].split("/")[1].strip()
                if "/" in subscriber_fields[0]
                else "",
                "DOB": subscriber_fields[1].strip().split("\n")[0]
                if subscriber_fields[1].strip()
                else "",
                "PayeeTaxID": payee_tax,
                "PayerID": payer_id,
            }
            patients.append(patient)

    return patients


def extract_notes(data_frames: List[pd.DataFrame]) -> str:
    """
    Extracts any notes found in the list of DataFrames.

    Args:
        data_frames (List[pd.DataFrame]): A list of DataFrames.

    Returns:
        str: A string containing any notes found.
    """
    notes = ""
    temp_list = [data_frame for data_frame in data_frames if len(data_frame.columns) == 1]
    for data_frame in temp_list:
        data_frame.columns = ["header"]
        if "EXPLANATION OF REMARKS" in data_frame["header"][0]:
            notes_ele = data_frame["header"].to_list()
            notes += " ".join(notes_ele[1:])

    notes = notes.replace("\r", " ")

    return notes


def get_string(data_frame: pd.DataFrame) -> str:
    """
    Extracts a string representation of a single column DataFrame.

    Args:
        data_frame (pd.DataFrame): A single column DataFrame containing text data.

    Returns:
        str: A string representation of the DataFrame, in the format
        "column_name, value1 value2 value3 ...".
    """
    col_name = data_frame.columns[0]

    text = f"{col_name}, {' '.join(data_frame[col_name].to_list())}"

    return text


def extract_payer_payee_details_from_pdf(filepath: str) -> Tuple[str, Dict, Dict]:
    """
    Extracts payer and payee details from a PDF file.

    Args:
        filepath (str): The path to the PDF file.

    Returns:
        Tuple[Any, Any, Any]: A tuple containing payer contact number,
        payer address details, and payee address details.
    """
    dfs = tabula.read_pdf(
        filepath,
        guess=False,
        pages=[1, 2],
        stream=True,
        encoding="utf-8",
        area=[(36, 80, 97, 372), (112, 80, 190, 372), (69, 318, 133, 553)],
        multiple_tables=True,
    )
    payer_df = dfs[0]
    payee_df = dfs[1]
    payer_contact = dfs[-1]

    payer_contact.columns = ["key", "value"]

    payer_contact_num = payer_contact.iloc[-1]["value"] if not None else ""

    payer_name = get_string(payer_df)

    payee_name = get_string(payee_df)

    payer_address_details = extract_address_details(payer_name)
    payee_address_details = extract_address_details(payee_name)

    return payer_contact_num, payer_address_details, payee_address_details


def generate_eft_patients(eft_check_date: str, claim_master: List[Dict]) -> List[Dict]:
    """
    Generates a list of dictionaries representing EFT patients based on the given EFT
    check date and claim master data.

    Args:
        eft_check_date (str): The EFT check date is date.
        claim_master (List[Dict]): A list of dictionaries representing the claim master data.

    Returns:
        List[Dict]: A list of dictionaries representing EFT patients.
    """

    patients = []

    for i, patient in enumerate(claim_master):
        patient_name_ = patient.get("PatientName", "")
        first_name = patient_name_.split()[0] if patient_name_ else ""
        last_name = patient_name_.split()[-1] if patient_name_ else ""
        provider = patient.get("RenderingProvider", "").split(",")[0]
        provider = provider.split(",")[0] if "," in provider else provider

        patients.append(
            {
                "ProviderClaimId": patient.get("ProviderClaimId", ""),
                "PatientFullName": patient_name_,
                "PayerClaimId": patient.get("PayerClaimId", ""),
                "MemberNo": patient.get("PatientAccountNumber", ""),
                "PayerPaid": patient.get("TotalAmount", ""),
                "SubscriberID": patient.get("SubscriberID", ""),
                "RenderingProviderFirstName": provider.split()[0],
                "RenderingProviderLastName": provider.split()[-1],
                "PatientName": patient.get("PatientName", ""),
                "ServiceDate": patient.get("ServiceDate", ""),
                "RenderingProviderID": patient.get("RenderingProviderID", ""),
                "EFT_CheckNumber": patient.get("EFT_CheckNumber", ""),
                "EFT_CheckDate": eft_check_date,
                "PatientFirstName": first_name,
                "PatientLastName": last_name,
                "Enrollee_ClaimID": "",
                "OtherAdjustments": "",
                "PlanType": patient.get("InsurancePlanType", ""),
                "RecordID": i,
            }
        )

        print(
            f"Patient added to EFTPatients for PAtientName\
                    ++++++++++++++++ {patient.get('PatientName')}\n"
        )

    return patients


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


def main(data):
    """
    main function to call all imp functionality
    Args:
        data: data from scrapper output

    Returns:
        wrapper output

    """

    print("Wraper Initiated for MCNA \n")

    url = data["EFTPatients"][0]["url"].replace("%20", " ")
    print(f"url is ------ {url}\n")

    eft_check_number = data["EFTPatients"][0]["CheckNumber"]

    eft_check_date = data["EFTPatients"][0]["EFTCheckDate"]

    filepath = filedownload_(url)

    options = {"lattice": True, "guess": True, "encoding": "ISO-8859-1"}

    data_frames = tabula.read_pdf(
        filepath, **options, pages="all", pandas_options={"header": None}
    )

    df_list = [df for df in data_frames if len(df.columns) == 17]

    total_master, claim_details = process_claim_details(df_list)

    patients = parse_patients_from_pdf(filepath)

    claim_master = [{**a, **b} for a, b in zip(patients, total_master)]

    notes = extract_notes(data_frames)

    payer_contact_num, payer_address_details, payee_address_details \
        = extract_payer_payee_details_from_pdf(filepath)

    for item in claim_master:
        item.update(
            {
                "Payer": payer_address_details.get("Item", ""),
                "PayerName": payer_address_details.get("ItemName", ""),
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
                "Notes": notes,
                "GroupId": "",
                "CheckNo": eft_check_number,
                "EFT_CheckNumber": eft_check_number,
                "EFT_CheckDate": eft_check_date,
                "url": url,
                "SubscriberName": "",
                "PayerClaimId": "",
                "PayerContact": payer_contact_num,
                "ClaimStatus": "",
                "PaymentMethodCode": "",
                "TransactionFee": "$0.00",
            }
        )

        print(
            f"claim added for claim master for PatientName ------------{item.get('PatientName')}\n"
        )

    for claim in claim_details:
        code = claim.get("CDT / Description")
        if code is not None:
            proc_code, procedure_details = (
                code.split("/") if len(code.split("/")) == 2 else ("", "")
            )
            claim.update(
                {
                    "ProcCode": proc_code.strip(),
                    "ProcedureDetails": procedure_details.strip(),
                    "ActualAllowed": "",
                    "OtherAdjustments": "",
                    "PayerInitiatedReductions": "",
                    "Enrollee_ClaimID": "",
                    "EFT_CheckNumber": eft_check_number,
                    "Adjustments": "",
                    "PatientPays": "",
                }
            )

        print(
            f"claim added for claim details for MemberNo >>>>>>>>>>>>>{claim.get('MemberNo')}\n"
        )


        patients = generate_eft_patients(eft_check_date, claim_master)

    json_data = {
        "EFTPatients": patients,
        "PpEobClaimMaster": claim_master,
        "PpEobClaimDetail": claim_details,
    }

    for i, (claim1, claim2, claim3) in enumerate(
        zip(
            json_data["EFTPatients"],
            json_data["PpEobClaimMaster"],
            json_data["PpEobClaimDetail"],
        ),
        start=1,
    ):
        claim1["RecordID"] = i
        claim2["RecordID"] = i
        claim3["RecordID"] = i

    return json_data
