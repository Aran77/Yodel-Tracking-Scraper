from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import time
import db as db
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

#get the year
year = str(datetime.today().year)

#quit program function
def on_quit():
    window.destroy()

#updates the status bar with user updates
def update_status(text):
    status_text.set(text)

#create main Tkinter window
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

def update_progressbar(pbar, value):
    pbar.config(value=value)
    pbar.update()
    print(value)
    if value == 100:
        pbar.pack_forget()

#handles the clicking of rows to get the tracking URL
def tree_click_handler(event):
    cur_item = data_table.item(data_table.focus())
    col = data_table.identify_column(event.x)
    window.clipboard_clear()
    window.clipboard_append('https://www.yodel.co.uk/tracking/'+ cur_item['values'][1] + "/"+ cur_item['values'][7])

#calculate difference in dispatch to cureent day/delivery day
def date_diff(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)

#Our main refresh function which clears the datatable and reloads from DB
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
        data_table.insert('', 'end', text=i, values=l)
    data_table.bind('<ButtonRelease-1>', tree_click_handler)
    update_status(str(len(d)) + " Consignments Loaded.")

#Remove an item from data table
def delete_item():
    if data_table.selection():
        selected_item = data_table.selection()[0] # get the selected item
        tmptn = data_table.item(selected_item, "values")[1]
        print(tmptn)
        confirm = messagebox.askyesno("Confirm","Are you sure you want to delete this item?")
        if confirm:
            data_table.delete(selected_item) # delete the selected item
            c,conn = db.connect_to_db()
            db.updatedb(c, conn, "DTD", "NA",tmptn)
        else:
            return

#Main scraping function
def scrapethePage(tn, pc):
    url = 'https://www.yodel.co.uk/tracking'
    bigurl = url +'/' + tn + '/' +pc +'?headless=true'   
    response = requests.get(bigurl)
    soup = BeautifulSoup(response.text, 'html.parser')  
    if not soup.find("yodel-hero_tracking-form"):        
        target_divs = soup.find_all("div", class_="parcel-current-status-message")
        for div in target_divs:
            content = div.get_text()
            status = content.strip()
            if status[:30] == "Your parcel has been delivered":
                tmptarget_divs = soup.find_all("div", class_="parcel-status-delivered-date")  
            else:
                tmptarget_divs = soup.find_all("div", class_="parcel-status-value")  
            for tmpdiv in tmptarget_divs:
                content1 = tmpdiv.get_text()
                dd = content1.strip()
            if status[:30] == "Your parcel has been delivered":
                status = "Delivered"            
        return status, dd
    else:
        status = "Error"
        dd = "Error"
        return status, dd

#convert written data to yyy/mm/ddd
def convert_written_date(written_date):
    day_of_week, day, month, year = written_date.split()
    month_number = datetime.strptime(month, '%B').month
    day = day[:-2]
    return f"{year}-{month_number}-{day}"

#load consignments in from FTP and then refresh the table
def getNewConsignments():
    #db.open_yodel_file()
    db.importfromFTP()
    populate_data()

#function to track consignment claims
def updateClaim():
    c,conn = db.connect_to_db()
    if data_table.selection():
        selected_item = data_table.selection()[0] # get the selected item
        current_values = data_table.item(selected_item)['values']
        tmptn = current_values[1]
        claim = current_values[11]
        print("Claim: " + str(claim))
        if claim == 1:
            db.update_claim(c,conn,tmptn,int(claim)-1)
            current_values[11] = 0
            data_table.item(selected_item, values=current_values)
            print("1 processed")
        elif claim == 0:
            db.update_claim(c,conn,tmptn,int(claim)+1)
            current_values[11] = 1
            data_table.item(selected_item, values=current_values)
            print("0 processed")
        else:
            db.update_claim(c,conn,tmptn,1)
            current_values[11] = 1
            data_table.item(selected_item, values=current_values)
            print("None processed")
        data_table.update()
        update_status("Claim Updated") 



#function to track consignment investigations
def updateInv():
    c,conn = db.connect_to_db()
    if data_table.selection():
        selected_item = data_table.selection()[0] # get the selected item
        current_values = data_table.item(selected_item)['values']
        tmptn = current_values[1]
        inv = current_values[10]
        print("Inv: " + str(inv))
        if inv == 1:
            db.update_inv(c,conn,tmptn,int(inv)-1)
            current_values[10] = 0
            data_table.item(selected_item, values=current_values)
            print("1 processed")
        elif inv == 0:
            db.update_inv(c,conn,tmptn,int(inv)+1)
            current_values[10] = 1
            data_table.item(selected_item, values=current_values)
            print("0 processed")
        else:
            db.update_inv(c,conn,tmptn,1)
            current_values[10] = 1
            data_table.item(selected_item, values=current_values)
            print("None processed")
        data_table.update()
        update_status("Investigation Updated")       

#Main function to call API
def refreshData():
    update_status("Updating Statuses...")
    c,conn = db.connect_to_db()
    pbar.config(maximum=len(data_table.get_children()))
    pbar.start()
    increment = 100/len(data_table.get_children())
    cnt=0
    print(increment)
    for line in data_table.get_children():
        cnt+=increment
        d= data_table.item(line)["values"]
        tn = d[1]
        dd = d[2]
        pc = d[7]
        formatted_date = ""
        failures = []
        if pc != "Redacted":
            status, delivered = scrapethePage(tn,pc)
            #print("********** date: "+ delivered)
            if status[:30] == 'Your parcel has been delivered':                
                #formatted_date = convert_written_date(delivered +' '+ year)
                formatted_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
            else:
                if delivered != "Unavailable at this time" and delivered != "Today" and ":" not in delivered and "stop" not in status:
                    formatted_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                    # formatted_date = convert_written_date(delivered +' '+ year)                
                else:
                    formatted_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
            db.update_db(c,conn, status, formatted_date, tn)
            update_progressbar(pbar, cnt)
        else:
            failures.append(tn)
    pbar.pack_forget()
        
    if failures:
        db.message_box("Refresh Complete", "Refresh Complete with some errors\n" + failures)
    else:        
        populate_data()
        update_status("Refresh Complete")
        db.message_box("Refresh Complete", "Refresh Complete")

#defunct, this was our initial method to populate DB
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
            status, delivered = scrapethePage(tn,pc)
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

#Create Tkinter Layout
#Add a horizontal top bar to host our buttons
control_bar = tk.Frame(window)
control_bar.pack(side='top', fill='x')
#buttons
open_new_data_button = tk.Button(control_bar, text="Import New Consignments", command=getNewConsignments)
open_new_data_button.pack(side='left', padx='5')
get_statuses_button = tk.Button(control_bar, text="Refresh", command=refreshData)
get_statuses_button.pack(side='left', padx='5')
claim_button = tk.Button(control_bar, text="Claimed?", command=updateClaim)
claim_button.pack(side='left', padx='5')
inv_button = tk.Button(control_bar, text="Investigated?", command=updateInv)
inv_button.pack(side='left', padx='5')
delete_button = tk.Button(control_bar, text="Delete", command=delete_item, bg="red",fg="white")
delete_button.pack(side='left', padx='5')
quit_button = tk.Button(control_bar, text="Quit", command=on_quit)
quit_button.pack(side='right')
#create data table frame
data_table_frame = tk.Frame(window)
data_table_frame.pack(side='bottom', fill='both', expand=True)
data_table = ttk.Treeview(data_table_frame, selectmode='browse')
#add a veritacal scrollbar
pbar = ttk.Progressbar(window, orient="horizontal", mode="determinate")
pbar.pack(side=tk.TOP, fill=tk.X)
treeScroll = ttk.Scrollbar(data_table)
treeScroll.configure(command=data_table.yview)
data_table.configure(yscrollcommand=treeScroll.set)
treeScroll.pack(side='right', fill='both')
data_table.pack(side='top', fill='both', expand=True)
status = tk.Label(data_table_frame, textvariable=status_text, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status.pack(side=tk.BOTTOM, fill=tk.X)
#create headings for data_table
headings = ('ID','Tracking_Number', 'Dispatch_Date','Order_ID','Ex_Order_ID','Source','Service','Postcode','Status','Expected','Investigated', 'Claimed','Days')
data_table['columns'] = ('ID','Tracking_Number', 'Dispatch_Date','Order_ID','Ex_Order_ID','Source','Service','Postcode','Status','Expected','Investigated', 'Claimed','Days')
#parse headings into datatable
for i in headings:
    data_table.heading(i, text=i)
for i in headings:
    data_table.column(i, stretch=tk.YES, width=100)    
data_table.column("#0", width=0)

pbar.config(value=0)

#Populate Data is our main Fresh function
populate_data()

window.mainloop()
