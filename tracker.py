from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
from datetime import datetime, timedelta
import time
import array as arr
import re
from tinydb import TinyDB, Query, where
import db as db
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
import json

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = 'c:\python\chrome driver\chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
year = str(datetime.today().year)

def on_quit():
    driver.quit()
    window.destroy()

def update_status(text):
    status_text.set(text)

window = tk.Tk()
window.title("YodelTracker")
status_text = tk.StringVar()
status_text.set("Ready")
# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the 90% width and height
width = int(screen_width * 0.9)
height = int(screen_height * 0.9)

# Set the dimensions of the window
window.geometry(f"{width}x{height}")

def date_diff(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def populate_data():
    update_status("Loading Data...")
    c,conn = db.connect_to_db()
    d = db.open_pending_data(c)
    
    for row in data_table.get_children():
        data_table.delete(row)
    for i, inner_list in enumerate(d):
        l = list(inner_list)
        if inner_list[9]:
            days = date_diff(l[2], l[9])
            l.append(days)
        print(i, l)
        data_table.insert('', 'end', text=i, values=l)
    update_status(str(len(d)) + " Consignments Loaded.")

def fireitup(tn,pc):
    update_status("Processing..." + tn)
    url = 'https://www.yodel.co.uk/tracking'
    bigurl = url +'/' + tn + '/' +pc +'?headless=true'
    driver.get(bigurl)
    #driver.implicitly_wait(0.0)
                                              
    elements = driver.find_elements(By.XPATH,"/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[1]/div/div/div[2]")
    elements1 = driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]/div/div/div[2]')
    elements2 = driver.find_elements(By.XPATH, '/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[1]/div/div/div/div[2]')
    elemets3 = driver.find_elements(By.XPATH, "/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[1]/div/div/div[2]")
    if elements:
        if elements[0].is_displayed():
            tmpStatus = elements[0].get_attribute('innerHTML').strip()
        #    print('elements '+ tmpStatus)
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
            elif tmpStatus[:31] == "Your parcel is in transit":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
            elif tmpStatus == "Your parcel is at our national hub":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
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
            if tmpStatus[:31] == "Your parcel is out for delivery":
                status = tmpStatus
                dd = driver.find_element(By.XPATH,'/html/body/div/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
    elif elements3:
        print("element3")
        if elements2[0].is_displayed():
            tmpStatus = elements2[0].get_attribute('innerHTML').strip()
            if tmpStatus == "We need some more information about your address. Please chat with us.":
                status = tmpStatus
                dd = driver.find_element(Bt.XPATH, '/html/body/div[1]/div[3]/div[3]/div/div[1]/div[2]/div[2]/div/div/div[2]').get_attribute('innerHTML').strip()
    else:
        status = "Error"
        dd = "Error"
    print(tn + " "  + status)
    return status.strip(), dd.strip()

def convert_written_date(written_date):
    day_of_week, day, month, year = written_date.split()
    month_number = datetime.strptime(month, '%B').month
    day = day[:-2]
    return f"{year}-{month_number}-{day}"

def getNewConsignments():
    #db.open_yodel_file()
    db.importfromFTP()
    populate_data()

def refreshData():
    update_status("Updating Statuses...")
    c,conn = db.connect_to_db()
    for line in data_table.get_children():
        d= data_table.item(line)["values"]
        tn = d[1]
        dd = d[2]
        pc = d[7]
        failures = []
        if pc != "Redacted":
            status, delivered = fireitup(tn,pc)
            if status[:3] == 'Del':
                formatted_date = convert_written_date(delivered[:-6] +' '+ year)
            else:
                formatted_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                db.update_db(c,conn, status, formatted_date, tn)
        else:
            failures.append(tn)
    if failures:
        db.message_box("Refresh Complete", "Refresh Complete with some errors\n" + failures)
    else:
        update_status("Refresh Complete, " + len(datatable) + "consignments refreshed.")
    populate_data()

def importData():
    c,conn = db.connect_to_db()
    d = importfromFTP()
    failures =[]
    for x in d:
        tn = x['tn']
        dd = str(x['dd'])[:10]
        pc = x['pc'].replace(" ","")
        if pc != "Redacted":
            update_status("Querying Yodel..."+tn)
            status, delivered = fireitup(tn,pc)
            if status[:3] == 'Del':
                formatted_date = convert_written_date(delivered[:-6] +' '+ year)
            else:
                formatted_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
            update_db(c, status, formatted_date, x['tn'])
            date_diff = datetime.strptime(formatted_date, "%Y-%m-%d") - datetime.strptime(dd,"%Y-%m-%d")
            days = date_diff
        else:
            failures.append(tn)
        time.sleep(0)
    if failures:
        print('Failures:')
        print(failures)
    populate_data()

control_bar = tk.Frame(window)
control_bar.pack(side='top', fill='x')
open_new_data_button = tk.Button(control_bar, text="Import New Consignments", command=getNewConsignments)
open_new_data_button.pack(side='left')
get_statuses_button = tk.Button(control_bar, text="Refresh", command=refreshData)
get_statuses_button.pack(side='left')
report_button = tk.Button(control_bar, text="Report")
report_button.pack(side='left')
quit_button = tk.Button(control_bar, text="Quit", command=on_quit)
quit_button.pack(side='right')
data_table_frame = tk.Frame(window)
data_table_frame.pack(side='bottom', fill='both', expand=True)
data_table = ttk.Treeview(data_table_frame)
treeScroll = ttk.Scrollbar(data_table)
treeScroll.configure(command=data_table.yview)
data_table.configure(yscrollcommand=treeScroll.set)
treeScroll.pack(side='right', fill='both')
data_table.pack(side='top', fill='both', expand=True)

status = tk.Label(data_table_frame, textvariable=status_text, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status.pack(side=tk.BOTTOM, fill=tk.X)

headings = ('ID','Tracking_Number', 'Dispatch_Date','Order_ID','Ex_Order_ID','Source','Service','Postcode','Status','Expected','Days')
data_table['columns'] = ('ID','Tracking_Number', 'Dispatch_Date','Order_ID','Ex_Order_ID','Source','Service','Postcode','Status','Expected','Days')
for i in headings:
    data_table.heading(i, text=i)
for i in headings:
    data_table.column(i, stretch=tk.YES, width=100)
data_table.column("#0", width=0)
for i in headings:
    data_table.heading(i, text=i)

populate_data()
window.mainloop()
