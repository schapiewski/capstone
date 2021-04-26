from selenium import webdriver
import time
from functools import partial
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def SignIn(driver):
    driver.find_element_by_xpath('//*[@id="loginForm"]/form/div[1]/input').send_keys('hark')
    driver.find_element_by_xpath('//*[@id="loginForm"]/form/div[2]/input').send_keys('Password009')
    driver.find_element_by_xpath('//*[@id="loginForm"]/form/button').click()

def Add(stock):
    driver.find_element_by_xpath('//*[@id="inputStock"]').send_keys(stock)
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="submitStock"]').click()

def Delete(driver):
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div/table/tbody/tr/td[9]/button').click()

def package1(driver):
    driver.find_element_by_xpath('/html/body/div/div[2]/div/div/main/div[2]/div[2]/div/div[2]/button').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="deluxeConfirmation"]/div/div/div[3]/form/button').click()

def package2(driver):
    driver.find_element_by_xpath('/html/body/div/div[2]/div/div/main/div[2]/div[3]/div/div[2]/button').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="ultimateConfirmation"]/div/div/div[3]/form/button').click()


if __name__ == "__main__":
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(executable_path=r"C:\Users\harki\Downloads\chromedriver_win32\chromedriver.exe",options=options)
    
    driver.get('http://127.0.0.1:8000/login/')
    SignIn(driver)
    time.sleep(3)

    driver.get('http://127.0.0.1:8000/add_stock.html')
    Add('mmm')
    time.sleep(3)
    Add('rf')

    time.sleep(3)
    Delete(driver)
    time.sleep(3)

    driver.get('http://127.0.0.1:8000/pricing/')
    time.sleep(3)
    package1(driver)
    time.sleep(3)

    driver.get('http://127.0.0.1:8000/add_stock.html')
    Add('mmm')
    time.sleep(3)
    Add('all')
    time.sleep(3)
    Add('rf')
    time.sleep(3)
    Add('mo')
    time.sleep(3)

    driver.get('http://127.0.0.1:8000/pricing/')
    time.sleep(3)
    package2(driver)
    time.sleep(3)
    driver.get('http://127.0.0.1:8000/add_stock.html')
    time.sleep(3)
    Add('mo')
    time.sleep(3)
    Add('eog')
    time.sleep(3)
    Add('cci')