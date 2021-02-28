from selenium import webdriver
import time
import tkinter
from tkinter import Button, messagebox
from functools import partial
import sys

def SignIn(driver):
    ##You'll need to change the username and emails for every test to ensure account creation
    driver.find_element_by_xpath('/html/body/div/form/div[1]/input').send_keys('dkkocab')
    driver.find_element_by_xpath('/html/body/div/form/div[2]/input').send_keys('1103Irving')
    driver.find_element_by_xpath('/html/body/div/form/button').click()

def SearchStock(StockName, driver):
    driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/form/input[2]').send_keys(StockName)
    driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/form/button').click()
    time.sleep(6)
    driver.close()


def Begin(name):
    try: 
        stock = name.get()
        driver = webdriver.Chrome("C:/Users/Alex/Downloads/chromedriver_win32/chromedriver.exe")    ##Youll need to change this to match the address of where you installed Chromedriver
        driver.get('http://127.0.0.1:8000/')
        SignIn(driver)
        time.sleep(3)
        SearchStock(stock, driver)
        
        print('Tests Success!')

        
    except:
        print('Tests Failed')


if __name__ == "__main__":
    #Unfortunately, the API doesn't like mass amount of calls so only on stock can be tested at a time or crashes will occur

    root = tkinter.Tk()
    root.title("Automated Testing")
    root.geometry("500x250")

    #FORM
    lableName = tkinter.Label(root, text="Stock Name: ")
    lableName.grid(column = 0, row = 10, pady=10)
    stockName = tkinter.StringVar()
    nameEntered = tkinter.Entry(root, width=25, textvariable = stockName)
    nameEntered.grid(column = 1, row = 10, pady=10)
    startTest = Button(root, text="Run", command= partial(Begin,stockName ))
    startTest.grid(column = 25, row = 10)
    root.mainloop()
