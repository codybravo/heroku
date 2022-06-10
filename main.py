import os
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver=webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


from pip import main
import asyncio
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
import json
from datetime import datetime
import smtplib, ssl
import sys

# Increasing recursion limit
sys.setrecursionlimit(30000)
print(sys.getrecursionlimit())

# 1: Details for email
sender = 'danish@letsbonobo.com'
receivers = ['danishm306@gmail.com']

nw = datetime.now()

# Get all the appsheet links and its properties!
def getAppsheetProps():
    url = "https://data.mongodb-api.com/app/data-esqzh/endpoint/data/beta/action/find"

    payload = json.dumps({
        "collection": "appsheet-properties",
        "database": "appsheet",
        "dataSource": "appsheet-selenium",
        "projection": {

        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': 'Xlfb3uRvFvhyO2hVuc47cbqSy4MSeJmrw4GADm4OYrtdNz5N8U4Twz1Kwyc45jpE'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    apps = response.json()['documents']

    return apps

apps = getAppsheetProps()
# driver = webdriver.Chrome()

# 2: Authentication details for appsheet apps
user_name = "helpticket@hitech.in"
password = "xxxxxxx" # Please enter your password


data_to_insert = []
crashed_data_insert = []

# Functins to insert data into MongoDB
def dataInsertionHelper(data,database,collection):
    mycollection = database[collection]
    for item in data:
        x = mycollection.insert_one(item)
        print(x)

# Functins to insert data into MongoDB
def mongoInsertion(data,which_collection):
    print(data)
    import urllib
    from pymongo import MongoClient
    import pymongo

    # 3: Authentication details for MongDB Atlas 
    username = urllib.parse.quote_plus('bonobodata')
    password = urllib.parse.quote_plus('bonodev') 
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    client = pymongo.MongoClient(f'mongodb+srv://{username}:{password}@appsheet-selenium.mnbec.mongodb.net/appsync_time?retryWrites=true&w=majority')
    db = client
    mydb = db['appsheet']
    dataInsertionHelper(data,mydb,which_collection)

# Functions for clicking buttons    
def clickButton(elements,element_name1):
    try:
        elements.click()
    except:
        clickButton(driver.find_element_by_class_name(element_name1),element_name1)

# Function for inserting password
def sendKeys(creds,element_name):
    try:
        driver.find_element_by_name(element_name).send_keys(creds)
    except Exception as e:
        print("Error while trying to insert text in input fields",e)
        sendKeys(creds,element_name)

# Function to check whether app is down if up store sync time in list. 
def appDetailsCollector(start,app_title,app_name):
    try:
        if(bool(driver.find_element(By.CLASS_NAME, "ErrorPopup__details").is_displayed())): # If app is crashed!
            error_details = driver.find_element_by_class_name("ErrorPopup__details").get_attribute("innerHTML")
            end = time.time()
            crashed_data_insert.append(dict(zip(["app name","error message","at"],[app_name,error_details,datetime.now().strftime("%H:%M:%S")]))) 
            print(start,end,end-start) 
            print(crashed_data_insert,"Crashed Data to ionsert")
            print("App crashed",app_name,)
        elif(bool(driver.find_element(By.CLASS_NAME, "sr-only").is_displayed())): # If app opened!
            end = time.time()
            data_to_insert.append(dict(zip(["app name","sync time","at"],[app_name,end - start,datetime.now().strftime("%H:%M:%S")])))
            print(start,end,end-start) 
            print(data_to_insert,"Data to ionsert")
            print("App working",app_name,app_title)
            
        else: # if page is not loaded yet check again
            # print("I am logging else statement")
            time.sleep(1)
            appDetailsCollector(start,app_title,app_name)
            
    except Exception as e: # if anything goes wrong! check again.
        # print("I am logging exception statement")
        time.sleep(1)
        appDetailsCollector(start,app_title,app_name)


def mainFunction():
    count = 0
    for item in apps:
        app_name = item['app_name']
        app_link = item['app_link']
        app_title = item['title']
        driver.get(app_link)

        # First time authentication block
        if(count == 0):
            # Login Procedure
            print(driver.find_element_by_id("Google"))   
            clickButton(driver.find_element_by_id("Google"),"Google")
            sendKeys(user_name,"identifier")
            clickButton(driver.find_element_by_class_name("VfPpkd-vQzf8d"),"VfPpkd-vQzf8d")
            sendKeys(password,"password")
            clickButton(driver.find_element_by_class_name("VfPpkd-vQzf8d"),"VfPpkd-vQzf8d")
            print("ok")

        start = time.time()
        appDetailsCollector(start,app_title,app_name)
        count = count + 1

    # Data insertion block into database 
    if data_to_insert:
        # Inserting appsheet sync time data into database 
        mongoInsertion(data_to_insert,"appsheet-sync-time")
        # print("true","1",data_to_insert)
    else:
        print("false","1",data_to_insert)
    
    if crashed_data_insert:
        print("-------------------------------")
        # print("true","2",crashed_data_insert)
        notify_crash = ",".join(str(item['app name']) for item in crashed_data_insert)

        # Mail sending block for the crashed app
        try: 
            #Create your SMTP session 
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp.login("danish@letsbonobo.com","xxcxxx")
            # message = "Message_you_need_to_send"
            smtp.sendmail("danish@letsbonobo.com", "danishm306@gmail.com",notify_crash) 
            smtp.quit() 
            print ("Email sent successfully!")
        except Exception as ex: 
            print("Something went wrong....",ex)
        
        # calling function to insert crashed app details into database
        mongoInsertion(crashed_data_insert,"appsheet-crashed-data")
    else:
        # print("-------------------------------")
        print("false","2",crashed_data_insert)

    exit()
    

mainFunction()




