from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from Table import table_to_dict, neat, camel_case
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup as bs
import json
from time import sleep
from downloader import upload_to_blob
import traceback
from multiwindow import windowhandler
from selenium.common.exceptions import StaleElementReferenceException
import base64
import os


class Scraper:

    def __init__(self, browser: object, input_: dict, inputparm: dict, message_id: str, patientData: dict):

        self.input_ = input_
        self.browser = browser
        self.inputparm = inputparm
        self.message_id = message_id
        self.patientData = patientData

    # @log_decorator("Scraper Function")

    def replace_strings(self, string, *args):
        return string % args

    def Element_with_retry(self, xpath, webdriver_wait, max_retries=5, text=None, html=None, tag_name=None):
        for i in range(max_retries):
            try:
                element = webdriver_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                if text == True:
                    return element.text
                if html == True:
                    return element.get_attribute('outerHTML')

                if tag_name == True:
                    return element.tag_name
                t = element.get_attribute('outerHTML')
                return element
            except StaleElementReferenceException:
                print("retying stale ref errror_______________")
                sleep(1)
                if i < max_retries - 1:
                    continue
                else:
                    raise

    def keyupdater(self, df, mandatoryFields):

        if mandatoryFields != None:
            if type(df).__name__ == 'dict':
                for nam in mandatoryFields:
                    if nam not in list(df.keys()):
                        df.update({nam: ""})
                return df
            else:
                for dict in df:
                    for nam in mandatoryFields:
                        if nam not in list(dict.keys()):
                            dict.update({nam: ""})
                return df
        else:
            return df

    def clicker(self, wait, xpath):

        try:
            eleme_ = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            try:
                eleme_.click()
                print("clicked by selenium")
                return True
            except:
                try:
                    t = self.browser.execute_script(
                        "try{document.evaluate(arguments[0],document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.scrollIntoView();return true;}catch(err){return false;}",
                        xpath)
                    t = self.browser.execute_script(
                        "try{document.evaluate(arguments[0],document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click();return true;}catch(err){return false;}",
                        xpath)
                    if t == True:
                        print("clicked by java script")

                        return True
                    else:
                        return False
                except:
                    pass
        except:
            try:
                t = self.browser.execute_script(
                    "try{document.evaluate(arguments[0],document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.scrollIntoView();return true;}catch(err){return false;}",
                    xpath)
                t = self.browser.execute_script(
                    "try{document.evaluate(arguments[0],document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click();return true;}catch(err){return false;}",
                    xpath)
                if t == True:
                    print("clicked by java script under exception")
                    return True
                else:
                    print("clicked by java script under exception")
                    return False
            except:
                print("nothing worked")

    def jsclicker(self, wait, xpath):
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except Exception as e:
            print(e)
            print("waited for element to but not found  with selenium")
        try:
            self.browser.execute_script("window.scrollBy(0,500);")
            t = self.browser.execute_script(
                "try{document.evaluate(arguments[0],document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click();return true;}catch(err){return false;}",
                xpath)
            if t == True:
                print("clicked by java script")
                return True
            else:
                return False
        except:
            pass

    def flat(self, list_):
        main_keys = []
        for i in list_:
            keys = list(i.keys())
            for j in keys:
                main_keys.append(j)
        if len(main_keys) == len(list(set(main_keys))):
            data = {}
            for i in list_:
                data.update(i)
            return [data]
        else:
            return list_

    def Scrap(self):
        wait = WebDriverWait(self.browser, 7)

        data = {}
        for i in self.input_:
            self.browser.switch_to.window(self.browser.window_handles[0])
            print(i['DataContextName'], "___________________________________________________________")
            DataContextName_main = i['DataContextName']
            data[DataContextName_main] = []
            DataContextName = "temp"

            flatten = json.loads(i['XPath']).get('flatten')
            waitTime = json.loads(i['XPath']).get("waitTime")
            print(json.loads(i['XPath']))
            print(waitTime, "--------------")
            xpaths = json.loads(i['XPath']).get('Xpaths')

            if xpaths == None:
                xpaths = json.loads(i['XPath']).get('MultipleXpaths')
            multiple_elements_xpath = range(1)
            multiple_elements = json.loads(i['XPath']).get('MultiplElements')

            action = None
            textExtraction = None
            windowChanges = None

            if multiple_elements:
                multiple_elements_xpath = multiple_elements.get("multiple_elements_xpath")
                if multiple_elements_xpath:
                    try:
                        wait.until(EC.element_to_be_clickable((By.XPATH, multiple_elements_xpath)))
                    except:
                        break
                    if multiple_elements.get("multiple_elements_type") == None:
                        multiple_elements_xpath = [x.get_attribute("textContent") for x in
                                                   self.browser.find_elements(By.XPATH, multiple_elements_xpath)]

                    if multiple_elements.get("multiple_elements_type") == "XpathBased":
                        multiple_elements_xpath = self.browser.find_elements(By.XPATH, multiple_elements_xpath)

                    if multiple_elements.get("multiple_elements_type") == "HrefBased":
                        multiple_elements_xpath = [x.get_attribute("href") for x in
                                                   self.browser.find_elements(By.XPATH, multiple_elements_xpath)]
                        print(multiple_elements_xpath)
                # print(multiple_elements.get("multiple_elements_xpath"))
                if multiple_elements.get("Searchlist"):
                    multiple_elements_xpath = multiple_elements.get("Searchlist")
                if multiple_elements.get("queries"):
                    multiple_elements_xpath = multiple_elements.get("queries")["Inputs"]

                action = multiple_elements.get('action')
                textExtraction = multiple_elements.get('textExtraction')

            for element_ in multiple_elements_xpath:
                print(element_)
                self.browser.switch_to.window(self.browser.window_handles[0])
                data[DataContextName] = []
                innerText = ""
                if action == "Click":
                    sleep(2)
                    if multiple_elements.get("multiple_elements_type") == "XpathBased":
                        try:
                            element_.click()
                        except:
                            self.browser.execute_script("arguments[0].click();", element_)

                    elif multiple_elements.get("multiple_elements_type") == "HrefBased":
                        self.browser.get(element_)

                    else:
                        wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{element_}')]"))).click()

                if multiple_elements:
                    windowChanges = multiple_elements.get("windowChanges")
                    if windowChanges:
                        self.browser = windowhandler(self.browser)
                        wait = WebDriverWait(self.browser, 7)

                if textExtraction == True:
                    innerText = element_.text

                if action == "Sendkeys":
                    try:
                        InputElementsXpath = multiple_elements.get("InputElementsXpath")

                        element_input = self.Element_with_retry(InputElementsXpath, wait)
                        element_input.clear()
                        element_input.send_keys(element_)
                        preclicks = multiple_elements.get("PreSteps")
                        if preclicks:
                            if preclicks.get('Clicks'):
                                for clk in preclicks['Clicks']:
                                    print(clk, ">>>>>>>>>>>>>>>>>")
                                    self.clicker(wait, clk)
                        SearchButton = multiple_elements.get("SearchButtonXpath")
                        self.clicker(wait, SearchButton)
                    except Exception as e:
                        print(e)
                if action == "MultipleQueries":
                    print(element_)
                    for elem in element_:
                        print(json.dumps(elem, indent=4))
                        PreClicks = elem.get("PreClicks")
                        if PreClicks:
                            if len(PreClicks) != 0:
                                for clk in PreClicks:
                                    self.clicker(wait, clk)
                        input_xpath = elem.get("xpath")
                        Value = elem.get("value")

                        element_input = self.Element_with_retry(input_xpath, wait)
                        element_input.clear()
                        element_input.send_keys(Value)
                        #  sleep(5)
                        Clicks = elem.get("PostClicks")
                        if Clicks:
                            if len(Clicks) != 0:
                                for clk in Clicks:
                                    self.clicker(wait, clk)

                    SearchButton = multiple_elements.get("SearchButtonXpath")
                    self.clicker(wait, SearchButton)

                d = {}

                if waitTime != None:
                    print(waitTime, "--------------------------------------------------------")
                    wait = WebDriverWait(self.browser, waitTime)

                def extract(j):
                    scrap = True

                    add_info = j['AdditonalInfo']
                    key = add_info['fileds']
                    mandatoryfields = j['AdditonalInfo'].get("mandatoryfields")
                    type_ = j['AdditonalInfo'].get("type")
                    precolumns = j['AdditonalInfo'].get("PreColumns")
                    proccode = j['AdditonalInfo'].get("LoopElement")
                    if proccode:
                        name = proccode.get("fieldName")
                        d[name] = element_

                    window_number = j['AdditonalInfo'].get("windowChange")
                    window_number_before_clicks = j['AdditonalInfo'].get("window_number_before_clicks")

                    if window_number_before_clicks:
                        self.browser = windowhandler(self.browser, window_number_before_clicks)
                    window_print = j['AdditonalInfo'].get("window_print")
                    exceptionClick = j['AdditonalInfo'].get("ExceptionClick")
                    if exceptionClick != None:
                        for click in exceptionClick:
                            self.clicker(wait, click)
                    if add_info['Click'] != None:

                        for clk in add_info['Click']:
                            #  print(clk)
                            if "%s" in clk:
                                if "!@" in clk:
                                    clk, data12 = clk.split('!@')
                                    clk = self.replace_strings(clk, self.patientData.get(data12))
                            t = self.clicker(wait, clk)
                            if clk.startswith("//cigna-procedure-code-results-dental/div[1]/div/table/tbody"):
                                sleep(5)
                            print(clk)
                            print(t)
                            if t != True:
                                scrap = False
                            if j['AdditonalInfo'].get('AfterClickWait'):
                                print("wait after click" + str(j['AdditonalInfo'].get('AfterClickWait')))
                                sleep(j['AdditonalInfo'].get('AfterClickWait'))

                    window_number_after_clicks = j['AdditonalInfo'].get("window_number_after_clicks")

                    if window_number_after_clicks:
                        self.browser = windowhandler(self.browser, window_number_after_clicks)
                    multiple_elements_xpath_ = range(1)
                    multiple_elements_ = j.get('MultiplElements')

                    action = None
                    textExtraction = None
                    post_steps = None
                    if multiple_elements_:
                        multiple_elements_xpath_ = multiple_elements_.get("multiple_elements_xpath")
                        try:
                            if multiple_elements_.get("type"):
                                if multiple_elements_.get("type") == "SearchLoop":
                                    multiple_elements_xpath_ = multiple_elements_.get("multiple_elements_xpath")

                            else:
                                wait.until(EC.element_to_be_clickable((By.XPATH, multiple_elements_xpath_)))
                                multiple_elements_xpath_ = [x.get_attribute("id") for x in
                                                            self.browser.find_elements(By.XPATH,
                                                                                       multiple_elements_xpath_)]
                        except:
                            multiple_elements_xpath_ = range(1)

                            # print(multiple_elements.get("multiple_elements_xpath"))

                        action = multiple_elements_.get('action')
                        textExtraction = multiple_elements_.get('textExtraction')
                        post_steps = multiple_elements_.get("PostSteps")

                    for elem in multiple_elements_xpath_:
                        if action == "Click":
                            try:
                                elemm = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='{elem}']")))
                                self.clicker(wait, f"//*[@id='{elem}']")
                            except:
                                pass

                        if action == "Sendkeys":
                            sleep(2)
                            elemm = self.Element_with_retry(multiple_elements_.get("InputElementsXpath"), wait)
                            elemm.clear()
                            elemm.send_keys(elem)
                            sleep(1)
                            self.Element_with_retry(multiple_elements_.get("SearchButtonXpath"), wait).click()
                            sleep(3)
                            if multiple_elements_.get("PreSteps"):
                                if len(multiple_elements_.get("PreSteps")) != 0:
                                    clicks = multiple_elements_.get("PreSteps")['Clicks']
                                    for click_ in clicks:
                                        print(click_)
                                        res = self.jsclicker(wait, click_)

                                        print(res, "____")
                                        sleep(1)

                        xpath = j['xpath']

                        Heading_ = j.get('headingXpath')
                        if Heading_ is not None:
                            try:
                                if "%s" in Heading_:
                                    Heading_ = Heading_ % elem
                                Heading_ = self.Element_with_retry(Heading_, wait, text=True)
                            except:
                                Heading_ = ""
                        if j.get('headingname'):
                            Heading_ = j.get('headingname')
                        if window_number:
                            self.browser = windowhandler(self.browser, window_number)
                        JsInjectPrint = j['AdditonalInfo'].get("JsInjectPrint")

                        if JsInjectPrint:
                            self.browser.execute_script(JsInjectPrint)

                        if window_print == True:
                            print_settings = {
                                "recentDestinations": [{
                                    "id": "Save as PDF",
                                    "origin": "local",
                                    "account": "",
                                }],
                                "selectedDestinationId": "Save as PDF",
                                "version": 2,
                                "isHeaderFooterEnabled": False,
                                "isLandscapeEnabled": True
                            }
                            pdf_data = self.browser.execute_cdp_cmd("Page.printToPDF", print_settings)
                            file = os.path.join(os.getcwd(), 'download', 'main.pdf')
                            with open(file, 'wb') as file:
                                file.write(base64.b64decode(pdf_data['data']))
                            # self.browser.execute_script('window.print();')
                        GetPdfFromBase64 = j['AdditonalInfo'].get("GetPdfFromBase64")
                        if GetPdfFromBase64:
                            if window_number:
                                self.browser = windowhandler(self.browser, window_number)
                            if GetPdfFromBase64.get("Sleep"):
                                sleep(GetPdfFromBase64.get("Sleep"))
                            if GetPdfFromBase64.get("Script"):
                                pdf_data = self.browser.execute_script(GetPdfFromBase64.get("Script"))
                                file = os.path.join(os.getcwd(), 'download', 'main.pdf')
                                with open(file, 'wb') as file:
                                    file.write(base64.b64decode(pdf_data))

                        if j["AdditonalInfo"].get("JavaScript"):
                            obj_script = j["AdditonalInfo"].get("JavaScript")
                            BeforeSleep = obj_script.get("BeforeSleep")
                            if BeforeSleep:
                                sleep(BeforeSleep)
                            js_ = obj_script.get("js")
                            print(js_)
                            self.browser.execute_script(js_)
                            AfterSleep = obj_script.get("AfterSleep")
                            if AfterSleep:
                                sleep(AfterSleep)

                        if j["AdditonalInfo"].get("DeleteElement"):
                            self.browser.execute_script(
                                "var element = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;element.parentNode.removeChild(element);",
                                j["AdditonalInfo"].get("DeleteElement"))
                            sleep(3)
                        if len(xpath) != 0:
                            if scrap == True:
                                if "%s" in xpath:
                                    if "!@" in xpath:
                                        xpath, data11 = xpath.split('!@')
                                        xpath = self.replace_strings(xpath, self.patientData.get(data11))
                                GoBack = j['AdditonalInfo'].get("GoBack")
                                GoForward = j['AdditonalInfo'].get("GoForward")
                                if GoBack:
                                    self.browser.back()
                                if GoForward:
                                    self.browser.forward()
                                print(xpath)

                                try:

                                    print(j['AdditonalInfo'].get("waitTime"), "wait time--------------------")
                                    if j['AdditonalInfo'].get("waitTime", 7) == 0:
                                        print("ignored.....")

                                    else:
                                        try:
                                            WebDriverWait(self.browser, j['AdditonalInfo'].get("waitTime", 7)).until(
                                                EC.presence_of_element_located((By.XPATH, xpath)))
                                        except:
                                            pass

                                    if self.Element_with_retry(xpath, WebDriverWait(self.browser,
                                                                                    j['AdditonalInfo'].get("waitTime",
                                                                                                           7)),
                                                               tag_name=True) == 'table':

                                        html = self.Element_with_retry(xpath, WebDriverWait(self.browser,
                                                                                            j['AdditonalInfo'].get(
                                                                                                "waitTime", 7)),
                                                                       html=True)

                                        data_ = table_to_dict(html, type_, precolumns)
                                        # print(data_)
                                        print(json.dumps(data_, indent=4))

                                        if type(data_).__name__ == 'dict':
                                            # if dictionary
                                            if len(key) != 0:
                                                df = pd.DataFrame([data_]).set_axis(key, axis=1, inplace=False).to_dict(
                                                    'records')
                                            else:
                                                df = data_
                                            print(json.dumps(self.keyupdater(df, mandatoryfields), indent=4))
                                            for data1 in df:
                                                data[DataContextName].append(self.keyupdater(data1, mandatoryfields))
                                        if len(key) != 0:  # if list
                                            df_ = pd.DataFrame(data_).set_axis(key, axis=1, inplace=False).to_dict(
                                                'records')
                                            print(json.dumps(df_, indent=4))

                                            if Heading_ == None:

                                                for du in df_:
                                                    data[DataContextName].append(self.keyupdater(du, mandatoryfields))
                                            else:
                                                temp_data = []
                                                for du_ in df_:
                                                    temp_data.append(self.keyupdater(du_, mandatoryfields))
                                                data[DataContextName].append({Heading_: temp_data})

                                        else:
                                            if Heading_ == None:

                                                for dc in data_:
                                                    data[DataContextName].append(self.keyupdater(dc, mandatoryfields))
                                            else:

                                                temp_data = []
                                                for du_ in data_:
                                                    temp_data.append(self.keyupdater(du_, mandatoryfields))
                                                data[DataContextName].append({Heading_: temp_data})

                                    else:
                                        if type(key).__name__ == 'list':
                                            html = self.Element_with_retry(xpath, wait, html=True)
                                            soup = bs(html, "html.parser")
                                            rows = soup.find().findAll(recursive=False)
                                            final_rows = []
                                            for i in rows:
                                                for z in i.findAll(recursive=False):
                                                    final_rows.append(
                                                        [neat(x.text) for x in z.findAll(recursive=False)])

                                            if len(final_rows[0]) == 2:
                                                df = pd.DataFrame(final_rows)

                                                if len(key) != 0:
                                                    df = pd.DataFrame([dict(zip(df[0], df[1]))]).set_axis(key, axis=1,
                                                                                                          inplace=False).to_dict(
                                                        'records')
                                                else:
                                                    df = [dict(zip([camel_case(neat(x)) for x in df[0]], df[1]))]
                                                for sv in df:
                                                    data[DataContextName].append(self.keyupdater(sv, mandatoryfields))

                                            else:
                                                df = pd.DataFrame(final_rows).to_dict('records')
                                                if len(key) != 0:
                                                    df = pd.DataFrame(final_rows).set_axis(key, axis=1,
                                                                                           inplace=False).to_dict(
                                                        'records')
                                                for dc in df:
                                                    data[DataContextName].append(self.keyupdater(dc, mandatoryfields))

                                        else:
                                            value = self.Element_with_retry(xpath, WebDriverWait(self.browser,
                                                                                                 j['AdditonalInfo'].get(
                                                                                                     "waitTime", 7)),
                                                                            text=True)
                                            d[key] = value
                                            print(d)

                                except Exception as e:
                                    if type(key).__name__ == 'str' and len(key) > 0:
                                        d[key] = ""
                                    print(e)
                                    print(traceback.format_exc())

                        if post_steps != None:
                            if len(post_steps) != 0:
                                clicks = post_steps.get("Clicks")
                                if len(clicks) != 0:
                                    for click_ in clicks:
                                        res = self.clicker(wait, click_)
                                        print(res, click_, "poststep")

                data[DataContextName] = []
                for j in xpaths:

                    if type(j).__name__ == "list":

                        data[DataContextName] = []
                        d = {}
                        for x in j:
                            extract(x)
                        if len(d) != 0:
                            print(d)
                        data[DataContextName].append(d)
                        data[DataContextName_main].append(data[DataContextName])
                        data[DataContextName] = []
                        d = {}


                    else:
                        extract(j)

                if len(d) != 0:
                    print(d)
                    data[DataContextName].append(d)

                files_ = upload_to_blob(self.inputparm, self.message_id)
                print(files_)

                if len(files_) == 1:
                    if type(data[DataContextName]).__name__ == 'list':
                        if type(data[DataContextName][0]).__name__ == 'list':
                            data[DataContextName][0][0].update({"url": files_[0]["url"]})
                        else:
                            data[DataContextName][0].update({"url": files_[0]["url"]})
                    else:
                        data[DataContextName].update({"url": files_[0]["url"]})
                if len(files_) > 1:
                    if type(data[DataContextName]).__name__ == 'list':
                        if type(data[DataContextName][0]).__name__ == 'list':
                            data[DataContextName][0][0].update({"url": [x["url"] for x in files_]})
                        else:
                            data[DataContextName][0].update({"url": [x["url"] for x in files_]})
                    else:
                        data[DataContextName].update({"url": [x["url"] for x in files_]})

                if flatten == True:
                    data[DataContextName] = self.flat(data[DataContextName])

                for dat_ in data[DataContextName]:
                    data[DataContextName_main].append(dat_)

            # if len(data[DataContextName_main])==1  and type(data[DataContextName_main]).__name__ == "list":
            #     data[DataContextName_main].append(data_extracted[0])

        try:
            del data["temp"]
        except:
            pass

        return data