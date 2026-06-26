from asyncio.windows_events import NULL
import sqlite3 
conn = sqlite3.connect('MasterDB.db')
c = conn.cursor()

def Current_Tier(id,name,Default_tier):
    # This function is used to change the default tier of the customer if needed
    print(f"Current Default Tier for {name} is {Default_tier}")
    
    
    

def present_CX_List():
    # Presents Customers and returns Customer Count
    c.execute("SELECT * FROM Customers")
    print(f"{'ID':<5} | {'Name':<20} ")
    print("-" * 70)
    
    count = 0
    for row in c.fetchall():
        count += 1
        print(f"{row[0]:<5} | {row[1]:<20} ")
    print("-" * 70 + "\n")
    return count

def handle_existing_customer():
    # Loops until a valid existing customer ID is selected
    #returns the selected customer ID
    customer_count = present_CX_List()
    while True:
        c_input = input(f"Choose the cx from the list above:\n: ").strip()
        
        try:
            c_id = int(c_input)
            
            c.execute("SELECT Name, Default_Tier FROM Customers WHERE cx_ID = ?", (c_id,))
            result = c.fetchone()
            
            if result:
                cx_name = result[0]
                cx_tier = result[1]
                print(f" Selected: {cx_name} (Tier: {cx_tier})")
                
                # We return a Tuple containing everything the next function needs
                return (c_id, cx_name, cx_tier)
            else:
                print(f" {c_id} is out of range. Try again.\n")
        except ValueError:
            print(" Please enter a valid number.\n")

def handle_new_customer():
    # Loops until we either confirm an existing name or finalize a new one
    # Returns either the new name (string) or the existing customer ID (int)
    while True:
        new_name = input("New customer name: ").strip().lower()
        
        # We SELECT cx_ID so we actually have the ID to show them!
        c.execute("SELECT cx_ID, Name FROM Customers WHERE Name = ?", (new_name,))
        result = c.fetchone()
        
        if result:
            cx_id = result[0]
            print(f"\n⚠️  {new_name} already exists! Customer ID in database is {cx_id}")
            x = input(f"Is this the correct customer? \n 1) Yes, use this customer \n 2) No, I want to enter another name \n: ").strip()
            
            if x == "1":
                print("✅ Routing back to the existing customer pipeline...")
                return cx_id # Returns the existing ID
            # If they choose 2 (or anything else), the loop restarts 
            if x != "2":
                print(" Invalid choice. Let's try that again.\n")
        else:
            print(f"✅ Proceeding with New Customer: {new_name}")
            return (0, new_name, unknown)

def Process1():
    # The Main Router
    while True:
        choice = input(f"Choose 1 for existing customer \nChoose 2 for new customer\n: ").strip()
        if choice == '1':
            selected_id, selected_name, tier = handle_existing_customer()
            current_tier = tier.strip().lower()
            
             
            x = input(f"""
                        Selected Customer ID = {selected_id} and Price Tier = {tier}.
                        would you like to keep default price tier or change it? \n
                        1) Keep Default \n
                        2) Change Price Tier 
                        : """).strip()
            if x == "1":
                print(f"✅ Keeping Default Price Tier = {tier}")

            elif x == "2":
                if current_tier == "retail":
                    current_tier = "wholesale"
                else:
                    current_tier = "retail"
                print(f"changd tier during this bill generation to {current_tier}")
            
            return (selected_id, selected_name, current_tier)    


        elif choice == '2':
            
            id,name,tier = handle_new_customer()
            
            if id == 0:
                # If id = 0, it means it's a new customer
                print(f"new customer name is : {name}")
                x = input(f"what do you want to use for the current tier for this customer? \n(1) retail or (2) wholesale) \n: ")
                if x == "1":
                    tier = "retail"
                elif x == "2":
                    tier = "wholesale"
            else:
                
                #if id != 0, it means the customer already exists, and current id and tier are true
                
                #do something with the existing customer name
                
                break
        else:
            print(f" '{choice}' is an invalid choice. Let's try that again.\n")

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