import sys

sys.path.append('imapsetup')

from flask import Flask,request,jsonify
from login import Login
from Search import Search
from Scraper import Scraper
from urllib.parse import urlparse
from main import kickoff
from azure_queue import QueueHandler
from base64 import b64encode,b64decode
import json
#test
app=Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():  
    #message = request.args.get('message')
    message = request.get_json()['message']
    message_id=request.get_json()['message_id']
    
    kickoff(message,message_id) 
    return 'success'                 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080, debug=False)