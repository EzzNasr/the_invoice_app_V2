import sqlite3
import Tablefunctions 
conn = sqlite3.connect('MasterDB.db')

c= conn.cursor()
Tablefunctions.PrintALL("Products")
# Tables for the database = 1) products which contains the prices , products , desc , 
c.execute("ALTER TABLE Products DROP COLUMN description")
conn.commit() 




conn.close()
