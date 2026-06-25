import sqlite3 
conn = sqlite3.connect('MasterDB.db')
c = conn.cursor()

def present_CX_List():
    #presents Customers and returns Customer Count
    c.execute(f"SELECT * FROM customers")
    print(f"{'ID':<5} | {'Name':<20} ")
    print("-" * 70)
    C = 0
    for row in c.fetchall():
        C+=1
        print(f"{str(row[0]):<5} | {str(row[1]):<20} ")
    print("-" * 70 + "\n")
    return C


def Process1():

    choice = input(f"choose 1 for existing customer \n choose 2 for new customer\n ").strip()

    if choice == '1':
        Customer_Count = present_CX_List()
        C = input(f"choose the cx from the list above( between 1 and {Customer_Count}) \n : ")

        if ( (C < 1) | C > Customer_Count ): 
            print(f"{C} is not a valid Customer ID \n")
            Process1()


    elif choice == '2':
            New_name = input("new customer name : ").strip().lower()
            
            c.execute(
            "SELECT 1 FROM Customers WHERE name = ?",
            (New_name,))
                       
            if c.fetchone():
                c.fetchone()[1]
                ID = 
                print(f"Name already exists and customer ID in database is {ID}")
            else:
                print("New customer")
                

    else :
        print(f"{choice} is an invalid choice")
        Process1()

def calculate_profit():
    # profit is total - cost price     
    print()

def bill_type():
    # 1 = mock , 2= Actual , 3 = Return 
    

    print(f"""
          
           please choose one of the following option for Bill Type \n 
          1) Mock Bill ( data will not be used in DataBase and will only output Bill for reference )\n
          2) Actual Bill ( data will be used in the final Database calculations in case of approval)\n
          3) Returned Bill ( Data Will subtract from DataBase based on the invoice number entered )\n
          
          """)
    
    Bill = input(f"\n:").strip()

    if Bill == "1" :

        print(f"we are in the mock Bill PipeLine \n")


        Process1()


    elif Bill == "2":

        print(f"we are in the Actuall Bill PipeLine \n")
        
        Process1()

    elif Bill == "3":
        
        print(f"we are in the Returned Bill PipeLine \n")
        
        Process1()
    
    else :
        
        print ("invalid option")
        
        bill_type()

def update_DB():
    print

bill_type()