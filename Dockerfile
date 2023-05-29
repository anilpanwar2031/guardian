FROM python:latest	

#ENV FLASK_APP=app.py
#ENV FLASK_ENV=development
# install google chrome
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable
RUN apt-get install -y default-jdk
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_108.0.5359.98-1_amd64.deb && apt install -y /tmp/chrome.deb && rm /tmp/chrome.deb

# install chromedriver
RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# ADD main.py .

WORKDIR /scraper
# install selenium
RUN pip install selenium==4.8.3

RUN pip install gunicorn==20.0.4

RUN pip install flask==2.1.0

RUN pip install imap-tools

RUN pip install azure.storage.queue

RUN pip install azure.storage.blob

RUN pip install azure-data-tables

RUN pip install easyimap	

RUN pip install lxml

RUN pip install usaddress

RUN pip install beautifulsoup4

RUN pip install pandas==1.5.3

RUN pip install requests
RUN pip install msal
RUN pip install openpyxl
RUN pip install nameparser
RUN pip install tabula-py
RUN pip install easyimap	
RUN pip install imap-tools
RUN pip install pdfservices-sdk

RUN pip install tika


COPY . .
EXPOSE 8080
CMD ["python3", "main.py"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app","--timeout", "3600"]

# CMD ["python", "./main.py"] 