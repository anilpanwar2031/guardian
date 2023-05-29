import os
import datetime
from blob import create_blob_from_message
import json

import random
import string


def getdata(key):
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        return data[key]





def upload_to_blob(InputParameters,message_id):
  
    date= ''.join(random.choices(string.ascii_uppercase +string.digits, k=10))
    
    path=os.getcwd()
    

    files=os.listdir("download")
    print(files,"here are the all files")
    urls=[]
    for file in files:
        filename=f"{InputParameters['AppName']}/{InputParameters['PayorName']}/{date}/{message_id}/{file}"       
        url=create_blob_from_message(InputParameters,filename, f"./download/{file}", 'pdf')        
        data={"filename": file,"url": url}
        urls.append(data)
        os.remove(f"./download/{file}")
    print(urls)    
    return urls