from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


def windowhandler(driver, number):
    windows = driver.window_handles
    count = 0
    while count < 100:
        try:
            driver.switch_to.window(driver.window_handles[number])
            driver.set_window_size(1920, 1080)
            driver.maximize_window()
            return driver
        except:
            sleep(0.05)
            count += 1
