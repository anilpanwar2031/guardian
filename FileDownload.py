from azure.storage.blob import BlobServiceClient
import json

filename = ""

def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]
    
def Downloader(AppName,filename,blob_url):
    json_data=getdata(AppName)
    connection_string =json_data["connect_str_blob"]
    container_name = json_data['container_name_blob']
  
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    _, blob_name = blob_url.split(container_name)
    blob_name = blob_name.strip('/')
    blob_client = container_client.get_blob_client(blob_name)
    #var1 = blob_client.download_blob()

    with open(filename, "wb") as f:
        download_stream = blob_client.download_blob()
        f.write(download_stream.readall())
        
# Downloader("Eligibility","main.pdf","https://sdeligibiltyscrappersa.blob.core.windows.net/eligibilty-scrapper-inc-blob/Eligibility/Cigna/F5D94RJ1DZ/8a7f3sd254221edssd/dddar.pdf")