import sqlite3
import functions 
conn = sqlite3.connect('MasterDB.db')
c= conn.cursor()


# Tables for the database :
#  1) "Products" which contains the Item ID, description, office price, and retail price
#  2) "Customers" which contains the cx_iD ,Name , Phone number, and default Tier (ie wholsale or retail)
#  3) "Orders" which is the overall layout of the bill Invoice Number , , Customer ID( linking to the Customers table), Date, and subtotal , discount, and total, profit , status ( active = ok , canceled = canceled)
#  4) "OrderDetails" which is the details of the order, linking to the Orders table via the Invoice Number, and linking to the Products table via the Item ID, and containing the quantity ordered, and the price sold 

c.execute('''CREATE TABLE IF NOT EXISTS Customers
              (cx_ID INTEGER PRIMARY KEY,
               Name TEXT NOT NULL,
               Phone_Number TEXT ,
               Default_Tier TEXT )''')



c.execute('''CREATE TABLE IF NOT EXISTS Orders
              (Invoice_Number INTEGER PRIMARY KEY AUTOINCREMENT,
               Customer_ID INTEGER NOT NULL,
               Date TEXT NOT NULL,
               Subtotal REAL NOT NULL,
               Discount REAL NOT NULL,
               Total REAL NOT NULL,
               Profit REAL NOT NULL,
               Status TEXT NOT NULL,
               FOREIGN KEY (Customer_ID) REFERENCES Customers(cx_ID))''')

c.execute('''CREATE TABLE IF NOT EXISTS OrderDetails
              (Invoice_Number INTEGER NOT NULL,
               Item_ID INTEGER NOT NULL,
               Quantity INTEGER NOT NULL,
               Price_Sold REAL NOT NULL,
               FOREIGN KEY (Invoice_Number) REFERENCES Orders(Invoice_Number),
               FOREIGN KEY (Item_ID) REFERENCES Products(Item_ID))''')

functions.ViewDB()

functions.ViewTable(f"Customers\n\n")
functions.ViewTable(f"Orders\n\n")
functions.ViewTable(f"OrderDetails\n\n")


conn.commit()
conn.close()
