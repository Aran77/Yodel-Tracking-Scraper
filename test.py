import sqlite3
from sqlite3 import Error
import json

dbfile = 'tracking.db'
#create the SQLite connection to our DB file
def connect_to_db():
  conn = sqlite3.connect(dbfile)
  # set our DB cursor
  c = conn.cursor()
  # return the cursor object
  return c, conn

c, conn= connect_to_db()
c.execute('''SELECT * FROM CONSIGNMENTS WHERE substr(status, 1, 3) != "Del"''')
data = c.fetchall()
for x in data:
    print(x)
print(len(data))
