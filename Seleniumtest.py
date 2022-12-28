#Import dependencies, Pandas fo Excel Sheets, Selenium for DOM interaction, datetime for time calculations, regedit for complex matching
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
from datetime import datetime, timedelta
import time
import array as arr
import re

#configure selenium options
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
#use the chrome driver!
DRIVER_PATH = 'c:\python\chrome driver\chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
#get current year for use with date calculations
year = str(datetime.today().year)

def fireitup(tn,pc):
    #confirgure URL for the tracking website
    url = 'https://www.yodel.co.uk/tracking'
    #add the tracking number and postcode from th ecxel file, headless=true gives a simpler verson of the tracking page
    bigurl = url +'/' + tn + '/' +pc +'?headless=true'
    driver.get(bigurl)    
    #brief wait for the dom to load
    driver.implicitly_wait(0.1)
    #there are three varying page layouts that are loaded depending on the consignment status, each of ythe follow are unique XPATHs to dom elements, we can use these to test the status of the page before trying to scrape the data
    elements = driver.find_elements(By.XPATH,"/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[1]/div/div/div[2]")
    elements1 = driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]/div/div/div[2]')
    elements2 = driver.find_elements(By.XPATH, '/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[1]/div/div/div/div[2]')
    #if the first element is present, check it is displayed and scrape the data into a local variable.
    if elements:
        if elements[0].is_displayed():
            tmpStatus = elements[0].get_attribute('innerHTML').strip()
            if tmpStatus == "We have updated your parcel with your neighbour preferences.":
                status = "Neightbour preference updated"
                dd = 'Expected delivery: ' + driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == "Your parcel has been delivered to a safe place":
                status = "Delivered, Safe Place" + ": " + driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[3]/div[2]').get_attribute('innerHTML').strip()
                dd = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[1]/div[2]').get_attribute('innerHTML').strip() + ' ' + driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == "Your parcel has arrived at the local delivery depot" or tmpStatus == "Your parcel has arrived at your local depot" or tmpStatus[:51] == 'Your parcel has arrived at the local delivery depot' or tmpStatus[:43] == "Your parcel is at your local delivery depot":
                status = "Local Depot"
                dd = 'Expected Delivery: ' +driver.find_element(By.XPATH, '/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == "Your parcel has been delivered" or tmpStatus == "Your parcel has been delivered through your letterbox":
                status = "Delivered"
                dd = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[1]/div[2]').get_attribute('innerHTML').strip() +' '+ driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == 'Your parcel has been delivered to your neighbour':
                status = "Delivered to Neighbour at " + driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[3]/div[2]').get_attribute('innerHTML').strip()
                dd = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[1]/div[2]').get_attribute('innerHTML').strip() + ' '+ driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus[:15] == "We're expecting":
                status = "Not Dispatched"
                dd = "n/a"
            elif tmpStatus == "Your parcel is on the way but the driver has experienced a short delay. Please check back for updates":
                status = "Short Delay"
                dd = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus[:31] == "Your parcel is out for delivery":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
    elif elements1:
        if elements1[0].is_displayed():
            tmpStatus = elements1[0].get_attribute('innerHTML').strip()
        #    print('Element1: '+ tmpStatus)
            if tmpStatus[:31] == "Your parcel is out for delivery":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == 'Your parcel is being loaded. Check back for updates shortly.':
                status = "Being loaded, check back soon"
                dd = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus[:11] == "Your driver":
                status = "Out for delivery today"
                dd = "Today"
    elif elements2:
        if elements2[0].is_displayed():
            tmpStatus = elements2[0].get_attribute('innerHTML').strip()
        #    print('Element2 '+ tmpStatus)
            if tmpStatus[:31] == "Your parcel is out for delivery":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
    else:
        status = "Error"
        dd = "Error"

    #print('Tracking Code ' + tn.strip() + ' | ' + pc + ' | Status ' + status + ' | ' + dd.strip())
    return status.strip(), dd.strip()

def convert_written_date(written_date):
    # Split the written date into its component parts
    day_of_week, day, month, year = written_date.split()
    # Convert the month to its numeric equivalent
    month_number = datetime.strptime(month, '%B').month
    # Remove the ordinal suffix from the day (e.g. "1st" -> "1")
    day = day[:-2]
    # Return the date in the desired format
    return f"{year}-{month_number}-{day}"

def importData():
    global df
    #load up the data file containing consignment details, Tracking number and Postcode and required.
    import_file_path = 'c:\\python\\YodelTracker\\yodel.xlsx'
    df = pd.read_excel (import_file_path)
    dds = []
    statuses = []
    dofd = []
    #Iterate through the dataframe, format data as required
    for index,row in df.iterrows():
        tn = row['Tracking Number']
        dd = str(row['Processed Date'])[:10] #only first 10 chars of date required.
        pc = row['Post Code'].replace(" ","") #remove space from barcode
        status, delivered = fireitup(tn,pc) #call the scraping function
        #if the consignment has been delivered then get the date it was delivered and work out ddays in transit, if not delivered get the current date and work out days in transit.
        if status[:3] == 'Del':
            formatted_date = convert_written_date(delivered[:-6] +' '+ year)
        else:
            formatted_date = datetime.strptime(datetime.now(), "%Y-%m-%d")
        date_diff = datetime.strptime(formatted_date, "%Y-%m-%d") - datetime.strptime(dd,"%Y-%m-%d")
        days = date_diff
        #add all the data to lists
        dds.append(delivered)
        statuses.append(status)
        dofd.append(days)
        time.sleep(0)
    #Insert the data lists into the Dataframe
    df.insert(len(df.columns),'Status', statuses)
    df.insert(len(df.columns),'Delivered on', dds)
    df.insert(len(df.columns), 'Days since dispatch', dofd)
    #save the updated dataframe to a new Excel File
    df.to_excel('YodelResults.xlsx')
    print(df)

def datediff(d1_str):
    #get todays date
    d2_str = datetime.today()
    #format that date
    d2 = d2_str.strftime("%Y-%m-%d")
    #get dispatch/processed date
    d1 = datetime.strptime(d1_str, '%Y-%m-%d')
    #minus one from the other to get difference.
    delta = d2 - d1
    return str(delta)

importData()
driver.quit()
