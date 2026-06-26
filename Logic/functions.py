import sqlite3 
conn = sqlite3.connect('MasterDB.db')
c = conn.cursor()

# =====================================================================
# GUI-READINESS REFACTOR (full explanation in chat)
# For each function below that mixed input()/print() with real logic,
# the logic has been pulled out into a new "_logic" / "get_*" function
# that takes plain arguments and returns a result or raises ValueError
# - no input(), no print(). That's what a future GUI calls directly.
# The original function keeps its exact name, signature, prompts,
# prints, and return values - it just now delegates the decision/query
# to the new pure function. CLI behavior is unchanged.
# Nothing in update_DB / calculate_profit / Process1 / bill_type was
# touched, since those are still stubs you're actively building out.
# =====================================================================

def Current_Tier_logic(cx_id, cx_name, default_tier, choice):
    # GUI-READY LOGIC (new): pure tier decision, no I/O.
    # choice must be the string "1" (keep/retail) or "2" (change/wholesale).
    # Raises ValueError on anything else so the caller (CLI loop today,
    # GUI form validation later) decides how to show the error.
    if cx_id != 0:
        current_tier = default_tier.strip().lower()
        if choice == "1":
            return (cx_id, cx_name, current_tier)
        elif choice == "2":
            new_tier = "wholesale" if current_tier == "retail" else "retail"
            return (cx_id, cx_name, new_tier)
        else:
            raise ValueError("Invalid choice. Please enter 1 or 2.")
    else:
        # cx_id == 0 means a brand new customer choosing their first tier
        if choice == "1":
            return (cx_id, cx_name, "retail")
        elif choice == "2":
            return (cx_id, cx_name, "wholesale")
        else:
            raise ValueError("Invalid choice. Please enter 1 or 2.")


def Current_Tier(cx_id, cx_name, default_tier):
    # GUI-READY REFACTOR: same prompts/prints/return values as before,
    # now delegates the actual decision to Current_Tier_logic() above.
    if cx_id != 0:
        current_tier = default_tier.strip().lower()
        while True:
            x = input(f"""
                Selected Customer: {cx_name} (ID: {cx_id}) | Default Tier: {current_tier}
                Would you like to keep default price tier or change it?
                1) Keep Default
                2) Change Price Tier 
                : """).strip()

            try:
                result = Current_Tier_logic(cx_id, cx_name, default_tier, x)
            except ValueError as e:
                print(f" {e}")
                continue

            if x == "1":
                print(f" Keeping Default Price Tier = {result[2]}")
            else:
                print(f" Changed tier during this bill generation to {result[2]}")
            return result

    elif cx_id == 0:
        # If id = 0, it means it's a completely new customer
        print(f" New customer name is: {cx_name}")
        while True:
            x = input(f"What do you want to use for the current tier for this customer?\n1) retail\n2) wholesale\n: ").strip()
            try:
                result = Current_Tier_logic(cx_id, cx_name, default_tier, x)
            except ValueError as e:
                print(f" {e}")
                continue
            return result
    

def get_customer_list():
    # GUI-READY LOGIC (new): pure DB read, no I/O.
    # Returns a tuple  of (cx_id, name) tuples for every customer - this
    # is what a GUI would call to populate a dropdown/table widget.
    c.execute("SELECT * FROM Customers")
    return [(row[0], row[1]) for row in c.fetchall()]


def get_customer_by_id(customer_id):
    # GUI-READY LOGIC (new): pure DB lookup, no I/O.
    # Returns (customer_id, name, tier) if found, otherwise None - a GUI can
    # call this directly off a dropdown selection instead of an input() loop.
    c.execute("SELECT Name, Default_Tier FROM Customers WHERE customer_id = ?", (customer_id,))
    result = c.fetchone()
    if result:
        return (customer_id, result[0], result[1])
    return None


def find_customer_by_name(name):
    # GUI-READY LOGIC (new): pure DB lookup, no I/O.
    # Returns the matching row (or None) for a customer with this name.
    #changed cx_ID to customer_id to match the table structure 
    c.execute("SELECT customer_id , Name FROM Customers WHERE Name = ?", (name,))
    return c.fetchone()


def present_CX_List():
    # GUI-READY REFACTOR: same printed table and same return value
    # (customer count) as before, now sourced from get_customer_list().
    #returns the number of customers in the database
    customers = get_customer_list()
    print(f"{'ID':<5} | {'Name':<20} ")
    print("-" * 70)
    for customer_id, name in customers:
        print(f"{customer_id:<5} | {name:<20} ")
    print("-" * 70 + "\n")
    return len(customers)


def handle_existing_customer():
    # GUI-READY REFACTOR: same prompts/prints/return value as before,
    # now delegates the DB lookup to get_customer_by_id() above.
    # Loops until a valid existing customer ID is selected
    #returns the selected customer ID
    customer_count = present_CX_List()
    while True:
        c_input = input(f"Choose the customer from the list above:\n: ").strip()
        
        try:
            customer_id = int(c_input)
            found = get_customer_by_id(customer_id)

            if found:
                cx_name = found[1]
                cx_tier = found[2]
                print(f" Selected: {cx_name} (Tier: {cx_tier})")
                
                # We return a Tuple containing everything the next function needs
                return found
            else:
                print(f" {customer_id} is out of range. Try again.\n")
        except ValueError:
            print(" Please enter a valid number.\n")


def handle_new_customer():
    # GUI-READY REFACTOR: same prompts/prints/return values as before,
    # now delegates the DB lookup to find_customer_by_name() above.
    # Loops until we either confirm an existing name or finalize a new one
    # Returns either the new name (string) or the existing customer ID (int)
    while True:
        new_name = input("New customer name: ").strip().lower()
        
        result = find_customer_by_name(new_name)
        
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
    # GUI-READY NOTE (no code change here): this function's only "logic"
    # is picking which handler to call based on the existing/new choice -
    # that choice IS the I/O step itself (a CLI prompt today, a button
    # click later), so there's nothing to extract into a separate pure
    # function. Once a GUI exists, this whole function gets replaced by
    # the GUI's own event handlers calling handle_existing_customer's /
    # handle_new_customer's logic counterparts and Current_Tier_logic()
    # directly - no wrapping needed.
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

def Validate_Products(product_ids):
    if not product_ids:
        return []

    placeholders = ','.join('?' * len(product_ids))
    query = f"SELECT id, name FROM Products WHERE id IN ({placeholders})"
    
    c.execute(query, tuple(product_ids))
    found_products = c.fetchall()
    
    found_ids = [row[0] for row in found_products]
    
    for p_id in product_ids:
        if p_id not in found_ids:
            print(f"Error: Product ID {p_id} does not exist in the database.")
            return False 
            
    return found_products

def Get_Product_IDs(): 
    print(f"\nEnter product IDs one by one. \n Type '-1' to exit.")
    product_ids = []
    
    # A loop for gathering the input
    while True:
        raw = input("> ").strip()
        
        if raw == '-1':
            break # Exit the input loop
            
        if not raw.isdigit():
            print("Invalid input. Please enter a numeric ID.")
            continue
            
        product_ids.append(int(raw))
        
    # Return the list, or False if they exited without typing anything
    return product_ids if product_ids else False


def Phase2_Process1():
    # 1. Get the customer state
    customer_id, Name, Tier = Phase1_Process1()
    
    # 2. Master Loop: Keep asking until we get a fully valid cart
    while True: 
       
        raw_user_input_ids = Get_Product_IDs() 
        
        # If they typed (nothing or garbage) False restart the master loop
        if not raw_user_input_ids:
            print("No valid items entered. Let's try again.")
            continue 

        # 3. Validate everything in ONE trip to the database
        valid_products = Validate_Products(raw_user_input_ids)
        
        if not valid_products:
            print("Validation failed invalid IDs where entered. Please re-enter your list.")
            
            # Loop restarts 
       
        else:
            # Everything passed , break out of the master loop.
            print(f"\nSuccess! Ready to process: {valid_products}")

            return Phase1_Process1(),  valid_products   # to phase 3 
    



    

def calculate_profit():
    # profit is total - cost price     
    print()


def Process1():
    cx_id, cx_name, cx_tier = Process1()


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


def update_DB():
    # This function is a placeholder for future database update logic
    print()
