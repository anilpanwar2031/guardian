import os
import os.path
import random
import string
import sys
import json
import logging
import re
import zipfile

import pandas as pd
import usaddress

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import (SdkException,
                                                               ServiceApiException,
                                                               ServiceUsageException)
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions



def extract_pdf_and_zip(input_pdf):
    """
    Extracts text and tables from a PDF file using Adobe's PDF Services API, saves the
    extracted data into a zip file, and returns the name of the zip file.

    Args:
        input_pdf (str): The path to the input PDF file.

    Returns:
        str: The name of the zip file that contains the extracted data.
    """

    output_zip = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".zip"

    if os.path.isfile(output_zip):
        os.remove(output_zip)

    try:

        # Initial setup, create credentials instance.
        credentials = Credentials.service_account_credentials_builder() \
            .from_file("pdfservices-api-credentials.json") \
            .build()

        # Create an ExecutionContext using credentials and create a new operation instance.
        execution_context = ExecutionContext.create(credentials)
        extract_pdf_operation = ExtractPDFOperation.create_new()

        # Set operation input from a source file.
        source = FileRef.create_from_local_file(input_pdf)
        extract_pdf_operation.set_input(source)

        # Build ExtractPDF options and set them into the operation
        extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
            .with_element_to_extract(ExtractElementType.TEXT) \
            .with_element_to_extract(ExtractElementType.TABLES) \
            .build()
        extract_pdf_operation.set_options(extract_pdf_options)

        # Execute the operation.
        result: FileRef = extract_pdf_operation.execute(execution_context)

        # Save the result to the specified location.
        result.save_as(output_zip)

        print("Successfully extracted information from PDF. Printing H1 Headers:\n")

        archive = zipfile.ZipFile(output_zip, 'r')
        print(archive.namelist())
        jsonentry = archive.open('structuredData.json')
        jsondata = jsonentry.read()
        data = json.loads(jsondata)
        for element in data["elements"]:
            if element["Path"].endswith("/H1"):
                print(element["Text"])

    except (ServiceApiException, ServiceUsageException, SdkException):
        logging.exception("Exception encountered while executing operation")

    return output_zip


def zip_processor(path):
    """
    Processes a zip file that contains multiple Excel files and a JSON file.

    Args:
        path (str): The path to the zip file.

    Returns:
        tuple: A tuple containing a list of pandas DataFrames, and a dictionary representing
        the structured data from the input JSON file. Each DataFrame in the list represents
        an Excel file in the zip archive that is located in the 'tables' directory. The
        dictionary contains the structured data from the input JSON file.

    """
    df_list = []

    with zipfile.ZipFile(path, 'r') as archive:
        table_files = [name for name in archive.namelist() if name.startswith('tables/') and name.endswith(".xlsx")]

        for name in table_files:
            with archive.open(name) as file:
                try:
                    df = pd.read_excel(file)
                    if df.columns.str.contains('_x000D_', case=False).any():
                        df = df.replace('_x000D_', '', regex=True)
                    df = df.rename(columns=lambda x: x.replace("_x000D_", ""))
                    df_list.append(df)
                except pd.errors.ParserError as e:
                    logging(f"Error parsing {name}: {e}")

        with archive.open('structuredData.json', 'r') as file:
            data = json.load(file)

    return df_list, data


def json_getter(json_data):
    """
    Extracts a subset of data from a JSON object and returns it as a new JSON object.

    Args:
        json_data (dict): A dictionary representing a JSON object.

    Returns:
        dict: A dictionary representing a JSON object that contains only the elements
        from the input JSON object that have a 'Text' key. Each element in the new JSON
        object has a 'text' key instead of 'Text' and a 'path' key instead of 'Path'.
        If the input JSON object is empty or does not have any elements with a 'Text'
        key, the output JSON object will be empty.

    Raises:
        ValueError: If the input data is not a dictionary or does not have an 'elements' key
        that maps to a list.

    Examples:
        #>>> json_data = {'elements': [{'Text': 'Hello', 'Path': '/greeting'},  ...  {'Text': 'World', 'Path': '/greeting'}]}

        #>>> json_getter(json_data)
        {'elements': [{'text': 'Hello', 'path': '/greeting'},  ...  {'text': 'World', 'path': '/greeting'}]}

    """
    if not isinstance(json_data, dict):
        raise ValueError('Input data must be a dictionary')

    elements = json_data.get('elements', [])

    if not isinstance(elements, list):
        raise ValueError('Input data must have an "elements" key that maps to a list')

    filtered_elements = [{'Text': item.get('Text'), 'Path': item.get('Path')} for item in elements if
                         item.get('Text') is not None]

    work_dict = {'elements': filtered_elements}

    return work_dict


def get_address_string(json_data, search_string):
    """
    Searches for a given string in the 'Text' key of each dictionary in a list of dictionaries obtained
    from a JSON file. If the string is found, concatenates the 'Text' value of the next 4 dictionaries
    in the list and returns the concatenated string.

    Args:
        json_data (dict): A dictionary obtained from a JSON file, where each value in the 'elements'
            key is a dictionary with a 'Text' key.
        search_string (str): The string to search for in the 'Text' key of each dictionary in json_data.

    Returns:
        str: A string containing the concatenated 'Text' values of the next 4 dictionaries in the list
            following the one where search_string was found. If search_string was not found or if there
            are less than 4 dictionaries remaining after the one where search_string was found, returns None.
    """
    search_index = -1

    for i, elem in enumerate(json_data["elements"]):
        if search_string in elem["Text"]:
            search_index = i
            break

    # If search_string is not found or at end of json_data, return None
    if search_index == -1 or search_index >= len(json_data["elements"]) - 4:
        return None

    # Look for the next 4 elements after "search_string"
    address_elements = json_data["elements"][search_index :search_index + 4]

    # Concatenate the text from these elements
    address_text = "".join(elem["Text"] for elem in address_elements)

    return address_text


def extract_payee_address(json_data):
    """
    Extracts the payee address from the input JSON data.

    Args:
        json_data (dict): A dictionary containing structured data in JSON format.

    Returns:
        str: The payee address as a string.
    """
    address_string = None
    elements = json_data.get('elements')
    if elements:
        for index, element in enumerate(elements):
            text = element.get('Text')
            if text and 'Your name,' in text and ', and Tax ID' in text:
                print(text)
                start_param = 'Your name, '
                end_param = ', and Tax ID'
                stripped_text = text[len(start_param): text.find(end_param)]
                print(stripped_text)
                for i in range(index):
                    prev_text = elements[i].get('Text')
                    if prev_text and stripped_text in prev_text:
                        address_string = get_address_string(json_data, stripped_text)
                        break
                if address_string:
                    break
    return stripped_text, address_string


# def basic_fields(url):
#     """
#     Downloads a PDF file from the given URL and returns the file path of the downloaded file.
    
#     Args:
#         url (str): The URL of the PDF file to download.

#     Returns:
#         str: The file path of the downloaded file.
#     """
#     file_path = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".pdf"
#     input_file = url.replace("%20", " ")
#     # Assuming Downloader function downloads the file from input_file URL to the file_path location.
#     # You can also add some error handling logic here in case the download fails.
#     Downloader('Payment Processing', file_path, input_file)

    
#     return file_path


def get_data_in_format(file_path):
    """
    Extracts data from a PDF and a ZIP file, processes it, and returns it in a specific format.

    Args:
        file_path (str): The file path of the PDF and ZIP files to extract data from.

    Returns:
        tuple: A tuple containing a list of Pandas data frames and a dictionary of processed JSON data.
    """
    # Extract PDF and ZIP files from file_path
    zip_file = extract_pdf_and_zip(file_path)

    # Process contents of ZIP file
    df_list, json_data = zip_processor(zip_file)

    # Process JSON data and return work_dict
    work_dict = json_getter(json_data)

    # Return list of data frames and work_dict dictionary
    return df_list, work_dict


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


def extract_address_details(address_text):
    try:
        address_list = usaddress.tag(address_text)[0]
    except usaddress.RepeatedLabelError as e:
            parsed_address = e.parsed_string
            print('parsed address is for payor is----------', parsed_address )
            address_list = get_address_list_when_exception(parsed_address)


    return {
        'Item': address_text,
        'ItemName': address_list.get('Recipient', ''),
        'AddressElements': get_address(address_text, address_list),
        'PlaceName': address_list.get('PlaceName', ''),
        'StateName': address_list.get('StateName', ''),
        'ZipCode': address_list.get('ZipCode', '')
    }


def process_list(lst: object) -> object:
    dicts = []
    for item in lst:
        if type(item) == dict:
            dicts.append(item)
        elif type(item) == list:
            dicts.extend(process_list(item))
    return dicts





