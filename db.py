import sqlite3
from sqlite3 import Error
import pandas as pd
from tkinter import filedialog as fd
import ftplib
from tkinter import messagebox
import time
import csv


dbfile = 'tracking.db'
#create the SQLite connection to our DB file
def connect_to_db():
  conn = sqlite3.connect(dbfile)
  # set our DB cursor
  c = conn.cursor()
  # return the cursor object
  return c, conn


""" DEFUNCT - KEEPING FOR STRUCTURE
def create_table(conn):
    try:
        conn.execute('''CREATE TABLE CONSIGNMENTS (ID INT PRIMARY KEY   NOT NULL,
            TN  TEXT   NOT NULL,
            DD  DATE   NOT NULL,
            OID TEXT   NOT NULL,
            EXID    TEXT,
            SOURCE  TEXT,
            SERVICE TEXT    NOT NULL,
            POSTCODE    TEXT    NOT NULL);''')
        print("Success")
    except Error as e:
        print(e)
    conn.close()
"""

# receive dictionary of values and insert to DB
def insert_to_db(d,c):
    try:
        c.execute('''INSERT INTO CONSIGNMENTS VALUES (?,?,?,?,?,?,?,?,?,?)''',(d['oid'],d['tn'], d['dd'],d['oid'],d['exid'],d['source'],d['service'],d['pc'],d['status'],d['ad']))
        print("Record Inserted. "+ str(d['oid']))
        c.commit()
    except Error as e:
        print(e)


def update_db(c,conn, status, ad, tn):
    c.execute('UPDATE CONSIGNMENTS SET STATUS = "'+ status +'", AD = "'+ ad +'" WHERE TN = "'+ tn +'"')
    conn.commit()


def open_pending_data(c):
    data = []
    c.execute('SELECT * FROM CONSIGNMENTS WHERE substr(status, 1, 3) != "Del"')
    data = c.fetchall()
    return data


def read_db(c):
    d = []
    c.execute('''SELECT * FROM CONSIGNMENTS WHERE STATUS IS NULL''')
    data = c.fetchall()
    print("Tracking  "+ str(len(data)) +" undelivered items")
    if len(data) > 0:
        for row in data:
            d.append({"oid": row[0], "tn": row[1], "dd" : row[2], "eid": row[4], "source" :row[5], "service": row[6], "pc": row[7]})

            #print("Order ID: ", row[0])
            #print("Tracking Number: ", row[1])
            #print("Dispatch Date: ", row[2])
            #print("External Order ID: ", row[4])
            #print("Source: ", row[5])
            #print("Service: ", row[6])
            #print("Postcode: ", row[7])
            #print("\n")

    else:
        print(str(len(data)) + " rows in table")
    return d


#Open the source file and grab the data we need. Send it to the insert_to_db function
def open_yodel_file():
    c,conn = connect_to_db()
    #prompt user for file path
    filetypes = (
    ('CSV files', '*.csv'),
    ('Text files', '*.text')
    )
    import_file_path = fd.askopenfilename(
        title='Choose data file',
        initialdir='/',
        filetypes=filetypes
    )
    #create pandas DF
    df = pd.read_csv (import_file_path)
    #move values to dictionary and send to DB in a loop
    for index,row in df.iterrows():
        if row['SubSource'] == "": row['SubSource'] = "Direct"
        if row['Postal Service'][:3] =="Yod":
            d = {
                "tn": row['Tracking Number'],
                "dd" : str(row['Processed Date'])[:10],
                "pc" : row['Post Code'].replace(" ",""),
                "exid" : row['External Reference'],
                "oid" : row['Order Id'],
                "source" : row['SubSource'],
                "service" : row['Postal Service'],
                "status": "",
                "ad": ""
            }
            # send data to the db
            print("Inserting into DB")
            insert_to_db(d,conn)


def importfromFTP():
    c,conn = connect_to_db()
    ftp = ftplib.FTP('ftp.devmysite.uk') # connect to the FTP server
    ftp.login('img@devmysite.uk', 'hXl%sOQ%D[R.') # login using the provided credentials
    ftp.cwd('/') # navigate to the folder containing the CSV file
    filename="ProcessedOrders.csv"
    with open(filename, 'wb') as f:
        ftp.retrbinary('RETR '+ filename, f.write) # download the CSV file to the local machine
        #ftp.delete(filename)
    if filename:
        data = pd.read_csv(filename)
        print(data.head())
        for index,row in data.iterrows():
            if row['SubSource'] == "": row['SubSource'] = "Direct"
            if row['Shipping service name'][:3] =="Yod":
                d = {
                    "tn": row['Tracking number'],
                    "dd" : str(row['Processed date'])[:10],
                    "pc" : row['Shipping postcode'].replace(" ",""),
                    "exid" : row['External reference'],
                    "oid" : row['Order Id'],
                    "source" : row['SubSource'],
                    "service" : row['Shipping service name'],
                    "status": "",
                    "ad": ""
                    }
                insert_to_db(d,conn)


def message_box(t, m):
    messagebox.showinfo(t,m)
