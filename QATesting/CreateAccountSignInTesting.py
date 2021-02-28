from selenium import webdriver
import time
import tkinter
from tkinter import messagebox

def createAccount(username, email):
    ##You'll need to change the username and emails for every test to ensure account creation
    driver.find_element_by_xpath('//*[@id="id_username"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="id_email"]').send_keys(email)
    driver.find_element_by_xpath('//*[@id="id_password1"]').send_keys('QAPassword')
    driver.find_element_by_xpath('//*[@id="id_password2"]').send_keys('QAPassword')
    driver.find_element_by_xpath('//*[@id="signupForm"]/form/button').click()

    driver.find_element_by_xpath('//*[@id="loginForm"]/form/div[1]/input').send_keys(username)
    driver.find_element_by_xpath('//*[@id="loginForm"]/form/div[2]/input').send_keys('QAPassword')
    driver.find_element_by_xpath('//*[@id="loginForm"]/form/button').click()

    print('Success!')

if __name__ == "__main__":
    try: 
        driver = webdriver.Chrome("C:/Users/Alex/Downloads/chromedriver_win32/chromedriver.exe")    ##Youll need to change this to match the address of where you installed Chromedriver
        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName15', 'QATestUser15@email.com' )
        time.sleep(3)

        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName16', 'QATestUser16@email.com' )
        time.sleep(3)

        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName17', 'QATestUser17@email.com' )
        time.sleep(3)

        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName18', 'QATestUser18@email.com' )
        time.sleep(3)

        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName19', 'QATestUser19@email.com' )
        time.sleep(3)

        driver.get('http://127.0.0.1:8000/signup/')
        createAccount('QAUserName20', 'QATestUser20@email.com' )
        time.sleep(3)
        driver.close()

        root = tkinter.Tk()
        root.withdraw()

        # Message Box
        messagebox.showinfo("Testing Results", "All tests ran succesfully!")
    except:
        root = tkinter.Tk()
        root.withdraw()

        # Message Box
        messagebox.showinfo("Testing Results", "Tests were unsuccessful")