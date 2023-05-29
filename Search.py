from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from time import sleep


class Search:

    def __init__(self,

                 browser,
                 pre_flow: dict,

                 post_flow: dict,
                 search_button_path: str,
                 queries: dict,
                 patient_data: dict,
                 search_filters: dict,

                 ):

        self.pre_flow = pre_flow
        self.browser = browser

        self.search_button_path = search_button_path
        self.post_flow = post_flow

        self.queries = queries

        self.patient_data = patient_data

        self.search_filters = search_filters

    # perfrom search only it consits 4 parts pre part of search if any  and post part after making query if any and additional inputs like dob with their relative XPATH as key pair value in dictionary

    def __str__(self):
        return f" query : {self.query}"

    # @log_decorator("search_function")
    def XpathCreator(self, inputxpath, data):
        xpath = inputxpath.replace("%s", data)
        return xpath

    def replace_strings(self, string, *args):
        return string % args

    # comment
    def performS(self):

        wait = WebDriverWait(self.browser, 20)
        if len(self.pre_flow) != 0:
            if len(self.pre_flow['AdditonalInfo']) != 0:
                if self.pre_flow['AdditonalInfo'].get('sleep'):
                    sleep(self.pre_flow['AdditonalInfo'].get('sleep'))
                if self.pre_flow['AdditonalInfo'].get("script"):
                    js = self.pre_flow['AdditonalInfo'].get("script").get("js")
                    arg1 = self.pre_flow['AdditonalInfo'].get("script").get("arg1")
                    arg2 = self.pre_flow['AdditonalInfo'].get("script").get("arg2")

                    try:
                        self.browser.execute_script(js, arg1, arg2)
                    except:
                        pass

            for step in self.pre_flow['Clicks']:

                # print("pre_flow step>>>>>>>>>>>>>>>>>>>",step)
                if "%s" in step:
                    if "!@" in step:
                        step, data = step.split('!@')[0], [step.split('!@')[1:]]
                        print(step, [self.patient_data.get(x) for x in data[0]])
                    step = self.replace_strings(step, *[self.patient_data.get(x) for x in data[0]])
                    # print("pre_flow step1>>>>>>>>>>>>>>>>>>>", step)

                ele = wait.until(EC.element_to_be_clickable((By.XPATH, step)))
                ele.click()

            if self.pre_flow.get('SleepAfterPreStep'):
                print("SleepAfterPreStep>>>>>>>>>>>>>>>>>>>>>", self.pre_flow['SleepAfterPreStep'])
                sleep(self.pre_flow['SleepAfterPreStep'])

        # self.browser.switch_to.window(self.browser.window_handles[1])

        if len(self.queries) != 0:

            for item in self.queries:
                if item.get('AdditonalInfo'):
                    if item['AdditonalInfo'].get("sleep"):
                        sleep(item['AdditonalInfo'].get("sleep"))
                q = self.patient_data[item['Data']]

                path = item['Xpath']

                PreClicks = item.get("PreClicks")
                PostClicks = item.get("PostClicks")

                # Double search option in website !!!!!!
                if type(q).__name__ == "list":
                    for qu in q:
                        if PreClicks != None:
                            for clk in PreClicks["Clicks"]:
                                print("preclk1>>>>>>>>>>", clk)
                                wait.until(EC.element_to_be_clickable((By.XPATH, clk))).click()
                        if item.get("sleep"):
                            sleep(item.get("sleep"))

                        ele = wait.until(EC.element_to_be_clickable((By.XPATH, path)))
                        ele.clear()
                        print("q>>>>>>>>>>>>>>>>>>1", q)

                        ele.send_keys(qu)

                        if item.get("SleepAfterInput"):
                            sleep(item.get("SleepAfterInput"))

                        if PostClicks != None:
                            for clk in PostClicks:
                                print(clk)
                                if "%s" in clk:
                                    if "!@" in clk:
                                        clk, data = clk.split('!@')
                                    clk = self.replace_strings(clk, self.patient_data.get(data))
                                print("clk1>>>>>>>>>>", clk)
                                wait.until(EC.element_to_be_clickable((By.XPATH, clk))).click()
                        if item.get("sleep"):
                            sleep(item.get("sleep"))

                else:

                    if PreClicks != None:
                        for clk in PreClicks["Clicks"]:
                            print("preclk2>>>>>>>>>>", clk)
                            wait.until(EC.element_to_be_clickable((By.XPATH, clk))).click()
                    if item.get("sleep"):
                        sleep(item.get("sleep"))
                    print(path)
                    ele = wait.until(EC.element_to_be_clickable((By.XPATH, path)))
                    ele.clear()

                    print("q>>>>>>>>>>>>>>>>>>2", q)
                    ele.send_keys(q)
                    if item.get("SleepAfterInput"):
                        sleep(item.get("SleepAfterInput"))
                    if PostClicks != None:
                        for clk in PostClicks:
                            if "%s" in step:
                                if "!@" in step:
                                    step, data = step.split('!@')[0], [step.split('!@')[1:]]
                                    print(step, [self.patient_data.get(x) for x in data[0]])
                                step = self.replace_strings(step, *[self.patient_data.get(x) for x in data[0]])
                            print("step>>>>>>>>>>>>>>>>>>>>>", step)
                            print("clk2>>>>>>>>>>", clk)
                            wait.until(EC.element_to_be_clickable((By.XPATH, clk))).click()
                    if item.get("sleep"):
                        sleep(item.get("sleep"))

        # making SEarach  here
        if len(self.search_button_path) != 0:
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, self.search_button_path))).click()
            except:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, self.search_button_path)))
                self.browser.execute_script("arguments[0].click();", button)

                # flow if any after query

        if len(self.post_flow) != 0:
            if len(self.post_flow['AdditonalInfo']) != 0:
                if self.post_flow['AdditonalInfo'].get('sleep'):
                    sleep(self.post_flow['AdditonalInfo'].get('sleep'))
            if self.post_flow['AdditonalInfo'].get("script"):
                js = self.post_flow['AdditonalInfo'].get("script").get("js")
                arg1 = self.post_flow['AdditonalInfo'].get("script").get("arg1")
                arg2 = self.post_flow['AdditonalInfo'].get("script").get("arg2")
                self.browser.execute_script(js, arg1, arg2)
            if self.post_flow.get("ExceptionClicks"):
                for step in self.post_flow['ExceptionClicks']:

                    if "%s" in step:
                        if "!@" in step:
                            step, data = step.split('!@')[0], [step.split('!@')[1:]]
                            print(step, [self.patient_data.get(x) for x in data[0]])
                        step = self.replace_strings(step, *[self.patient_data.get(x) for x in data[0]])
                    print("step>>>>>>>>>>>>>>>>>>>>>", step)
                    try:
                        wait.until(EC.element_to_be_clickable((By.XPATH, step))).click()
                        if self.post_flow.get("AfterExceptionSleep"):
                            sleep(self.post_flow.get("AfterExceptionSleep"))
                    except:
                        pass
            if self.post_flow['Clicks'] != None:
                print("self.post_flow['Clicks']>>>>>>>>>>>>>", self.post_flow['Clicks'])

                for step in self.post_flow['Clicks']:

                    if "%s" in step:
                        if "!@" in step:
                            step, data = step.split('!@')[0], [step.split('!@')[1:]]
                            print(step, [self.patient_data.get(x) for x in data[0]])
                        step = self.replace_strings(step, *[self.patient_data.get(x) for x in data[0]])
                    print("step>>>>>>>>>>>>>>>>>>>>>", step)
                    wait.until(EC.element_to_be_clickable((By.XPATH, step))).click()

            if len(self.post_flow.get('AdditonalInfo')) != 0:
                if self.post_flow['AdditonalInfo'].get('aftersleep'):
                    sleep(self.post_flow['AdditonalInfo'].get('aftersleep'))
                if self.post_flow.get('AdditonalInfo').get('afterwait') != None:
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, self.post_flow.get('AdditonalInfo').get('afterwait'))))

        if len(self.search_filters) != 0:
            print(self.search_filters)
            if self.search_filters.get("XpathGenerator"):

                XpathGenerator_ = self.search_filters.get("XpathGenerator")
                xpath = XpathGenerator_.get("XPath")
                datakey = XpathGenerator_.get("DataKey")
                waitfor = XpathGenerator_.get("wait")
                caps = XpathGenerator_.get("caps")
                data = self.patient_data[datakey]
                if caps:
                    data = data.upper()

                elif caps == False:

                    data = data.lower()

                xpath_ = self.XpathCreator(xpath, data)
                print(xpath_)
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath_))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, waitfor)))

            else:
                print(self.search_filters)
                script = self.search_filters['js']
                args1 = self.search_filters['arg1']
                args2 = ""
                if len(self.search_filters.get('arg2', "")) != 0:
                    if len(self.patient_data[self.search_filters['arg2']]) != 0:
                        args2 = self.patient_data[self.search_filters['arg2']]
                if self.search_filters.get('wait'):
                    wait.until(EC.element_to_be_clickable((By.XPATH, self.search_filters['wait'])))
                try:
                    t = self.browser.execute_script(script, args1, args2)
                except:
                    pass
                print(t, "--------------------------------------------------------")
                if self.search_filters.get('afterwait'):
                    wait.until(EC.element_to_be_clickable((By.XPATH, self.search_filters['afterwait'])))

                if self.search_filters.get('Clicks'):
                    for step in self.search_filters.get('Clicks'):
                        replace = []

                        if self.search_filters.get('replace'):
                            for data in self.search_filters.get('replace'):
                                print(data)
                                replace.append(self.patient_data[data])
                        print(replace)
                        print(step)
                        if "%s" in step:
                            step = self.replace_strings(step, *replace)

                        wait.until(EC.element_to_be_clickable((By.XPATH, step))).click()

                print(t, "--------------------------------------------------------")
                if self.search_filters.get("SleepAfterFilter"):
                    sleep(self.search_filters.get("SleepAfterFilter"))

# document.evaluate("//*[text()='813.00']/ancestor::tr[2]/td[4]/span, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()






