import os
from azure.storage.blob import BlobServiceClient, ContentSettings
import uuid
import json
import os

#from azure.storage.blob import AppendBlobService

def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]
        
    


def create_blob_from_message(InputParameters,file_name, message, textorpdf = 'text'):  
    config=getdata(InputParameters['AppName'])
    connect_str    =config['connect_str_blob']
    container_name =config['container_name_blob']
    sa_name        =config['sa_name_blob']
    storage_account_key=connect_str

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = container_name
    file_name = file_name
    message = message
    if textorpdf == 'text':
        cnt_settings = ContentSettings(content_type="text/plain")
    else:
        cnt_settings = ContentSettings(content_type="application/pdf")
        
        
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    
    try:
        # Create the container
        container_client = blob_service_client.create_container(container_name)
    except:
        print('INFO:CONTAINER_ALREADY_EXISTS')
    
    #Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    #Instantiate a ContainerClient
    container_client = blob_service_client.get_container_client(container_name)
    try:
        if textorpdf == 'text':
            blob_client.upload_blob(message, content_settings=cnt_settings)
        else:
            with open(message, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
    except:
        return 'ERROR: FILE_ALREADY_EXISTS'
    return blob_client.url



