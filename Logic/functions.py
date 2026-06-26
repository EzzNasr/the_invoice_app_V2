import sqlite3 
conn = sqlite3.connect('MasterDB.db')
c = conn.cursor()

def Current_Tier(cx_id, cx_name, default_tier):
    # This function safely traps the user until they give a valid tier choice
    
    if cx_id != 0:
        current_tier = default_tier.strip().lower()
        while True:
            x = input(f"""
                Selected Customer: {cx_name} (ID: {cx_id}) | Default Tier: {current_tier}
                Would you like to keep default price tier or change it?
                1) Keep Default
                2) Change Price Tier 
                : """).strip()
            
            if x == "1":
                print(f" Keeping Default Price Tier = {current_tier}")
                return (cx_id, cx_name, default_tier)
            elif x == "2":
                
                current_tier = "wholesale" if current_tier == "retail" else "retail"
                print(f" Changed tier during this bill generation to {current_tier}")
                break
            else:
                print(" Invalid choice. Please enter 1 or 2.")
                
        return (cx_id, cx_name, current_tier) 
        
    elif cx_id == 0:
        # If id = 0, it means it's a completely new customer
        print(f" New customer name is: {cx_name}")
        while True:
            x = input(f"What do you want to use for the current tier for this customer?\n1) retail\n2) wholesale\n: ").strip()
            if x == "1":
                current_tier = "retail"
                break
            elif x == "2":
                current_tier = "wholesale"
                break
            else:
                print(" Invalid choice. Please enter 1 or 2.")
                
        return (cx_id, cx_name, current_tier)
    
def update_DB():
    # This function is a placeholder for future database update logic
    print()


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
        c.execute("SELECT customer_id , Name FROM Customers WHERE Name = ?", (new_name,))
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
            return (0, new_name, None)

def Phase1_Process1():
    # this is the first part of the process1, handeling the customer classification ( existing or new ) and tier confirmation (Default or change)
    while True:
        choice = input("Choose 1 for existing customer \nChoose 2 for new customer\n: ").strip()
        
        if choice == '1':

            cx_id, cx_name, cx_tier = handle_existing_customer() 
            
        elif choice == '2':
            #Whether truly new or not same treatement, if id =0 this is my flag
            cx_id, cx_name, cx_tier = handle_new_customer()
            
        else:
            print(f"⚠️ '{choice}' is an invalid choice. Let's try that again.\n")
            continue # gets back to the top of the loop for a new choice

        #whether new or existing, we now have the customer name and ID, we can now check if they want to change the tier
        final_id, final_name, final_tier = Current_Tier(cx_id, cx_name, cx_tier)
        return (final_id, final_name, final_tier)

def Process1():
    cx_id, cx_name, cx_tier = Process1()


def calculate_profit():
    # profit is total - cost price     
    print()

def bill_type():
    #still not implemented, but this function will handle the bill type selection and routing to the appropriate processing pipeline
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


