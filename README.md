# Yodel Tracking Status Scraper
## The Problem

The Yodel API was not available to us, we needed another way to gather consignment tracking details, refresh them regularly and monitor the number of days in transit.
We also needed to a way to spot potential shipping issues.

## The Solution

I chose to use python for its rapid development style. The plan was to import a list of consignments into a database and call the yodel API, however, it was not cost effective for us. 
Instead I decided to opt for a scraper. Selenium was my first choice but I had issues with the XPaths and found it to be quite brittle. BeautifulSoup4 was the right choice in this use case.

## The Code
* I went with a SQLite Databse as the requirements for storing and accessing data are mininal.
* Tkinter is used to create a functional GUI
* BeautifulSoup4 is utilised for scraping the Yodel Tracking Page
* A Tkinter Treeview is used to display the tabular data
* Functions created to track the current state of our investigation and claim for lost parcels



### TO DO: 
~~Try using BeautifulSoup4 instead of selenium.~~

~~Keep list of undelivered items and count days since posted~~

~~Import from FTP, using Linnwork order managment to export the previous days processed orders to ftp~~

~~Implement multi-page tabs that show different statuses. For instance, One for 'pending consignments', one for 'delivered consignments' and one for 'lost but claimed for' consignments~~

~~Search Function - Super easy~~

~~CreatE email body copy and paste~~
