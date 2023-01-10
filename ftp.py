
import ftplib
import pandas as pd

ftp = ftplib.FTP('ftp.devmysite.uk') # connect to the FTP server
ftp.login('img@devmysite.uk', 'hXl%sOQ%D[R.') # login using the provided credentials

ftp.cwd('/') # navigate to the folder containing the CSV file

with open('ProcessedOrders.csv', 'wb') as f:
    ftp.retrbinary('RETR ProcessedOrders.csv', f.write) # download the CSV file to the local machine

ftp.quit() # close the FTP connection

# now that the file has been downloaded, read it into a DataFrame
df = pd.read_csv('ProcessedOrders.csv')

print(df.head()) # print the first five rows of the DataFrame
