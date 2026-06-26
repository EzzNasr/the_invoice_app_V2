import sqlite3
import yaml 
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
    
    # getting everything we need for later phases
    query = f"SELECT Product_ID, item_name, Retail_Price, Wholesale_Price, Cost FROM Products WHERE Product_ID IN ({placeholders})"

    
    c.execute(query, tuple(product_ids))
    found_products = c.fetchall()
    
    # saving IDs in a list
    found_ids = [row[0] for row in found_products]
    
    for p_id in product_ids:
        if p_id not in found_ids:
            print(f"Error: Product ID {p_id} does not exist in the database.")
            return False 
            
    # found product came from C.fetchall so it has everything included
    return found_products


def Get_Product_IDs(): 
    print(f"\nEnter product IDs one by one. \nType '-1' to exit.")
    product_ids = []
    
    while True:
        raw = input("> ").strip()
        
        if raw == '-1':
            break 
            
        if not raw.isdigit():
            print("Invalid input. Please enter a numeric ID.")
            continue
            
        product_ids.append(int(raw))
        
    return product_ids if product_ids else False


def Phase2_Process1():
    customer_id, Name, Tier = Phase1_Process1()
    
    while True: 
        raw_user_input_ids = Get_Product_IDs() 
        
        if not raw_user_input_ids:
            print("No valid items entered. Let's try again.")
            continue 

        
        valid_products = Validate_Products(raw_user_input_ids)
        
        if not valid_products:
            print("Validation failed. Invalid IDs were entered. Please re-enter your list.")
        else:
            print(f"\nSuccess! Ready to process: {valid_products}")
            # passing on the 4 needed 
            return customer_id, Name, Tier, valid_products  


def Bulk_system(valid_products, tier):
    while True:
        raw_qty = input("Enter the bulk quantity for ALL items: ").strip()
        if raw_qty.isdigit() and int(raw_qty) > 0:
            bulk_qty = int(raw_qty)
            break
        print("Invalid input. Please enter a positive whole number.")

    final_order_details = []

    for prod in valid_products:
        #prices are included in the tuple
        p_id = prod[0]
        p_name=prod[1]
        p_retail = prod[2]
        p_wholesale = prod[3]
        p_cost = prod[4]

        active_price = p_wholesale if tier.strip().lower() == "wholesale" else p_retail

        total_line_cost = p_cost * bulk_qty
        final_line_price = active_price * bulk_qty

        final_order_details.append((p_id, bulk_qty, total_line_cost ,final_line_price, p_name))
        # contains Product ID  ,Quantity , line COST ,   line price all  , Item name in a tuple for each item 

    return final_order_details


def Individual_system(valid_products, tier):
    final_order_details = []
    
    print(f"\nLet's set the quantities for each item.")
    
    for prod in valid_products:
        # Unpack the tuple provided by Phase 2
        p_id = prod[0]
        p_name = prod[1]
        p_retail = prod[2]
        p_wholesale = prod[3]
        p_cost = prod[4]
        
        # Pick the price based on the tier
        active_price = p_wholesale if tier.strip().lower() == "wholesale" else p_retail
        
        # Trap the user until they give a valid quantity for THIS specific item
        while True:
            # Added the name and price to the prompt so the user has context
            raw_qty = input(f"Enter quantity for '{p_name}' (ID: {p_id}) @ EGP {active_price:.2f}: ").strip()
            
            if raw_qty.isdigit() and int(raw_qty) > 0:
                item_qty = int(raw_qty)
                break
                
            print("Invalid input. Please enter a positive whole number.")
            
        # Calculate the final total for this specific item
        final_line_price = active_price * item_qty
        total_line_cost = p_cost * item_qty
        # Package it up and add it to our final cart
        final_order_details.append((p_id,item_qty, total_line_cost, final_line_price, p_name ,))
        # contains Product ID  ,Quantity , line COST ,   line price all  , Item name in a tuple for each item 
    return final_order_details


def Quantity_System(valid_products, tier):
    while True:
        choice = input("\nPress 1 for Bulk Quantity or 2 for Individual Quantity: ").strip()

        if choice == '1':
            print("\n--- Bulk Quantity Mode ---")
            return Bulk_system(valid_products, tier)
            
        elif choice == '2':
            print("\n--- Individual Quantity Mode ---")
            return Individual_system(valid_products, tier)
            
        else:
            print("Invalid choice. Please literally just press 1 or 2.")


def Phase3_Process1():
    # valid_products = # contains Product ID , Item name ,Quantity , line COST and  line price all in a tuple for each item 
    customer_id, Name, tier, valid_products = Phase2_Process1()

    final_cart = Quantity_System(valid_products, tier)
    
    print(f"\nPhase 3 Done. Going into discount and Totals.")
    print(final_cart)
    return final_cart
    

def Calculate_Subtotal(final_cart):
        # contains Product ID  ,Quantity , line COST ,   line price all  , Item name in a tuple for each item 

    # This extracts index 3 from every item and sums them instantly
    subtotal = sum(item[3] for item in final_cart)
    
    return subtotal


def Apply_Discount(subtotal):
    """
    GUI Prototype: Traps the user until a valid flat or % discount is applied.
    Returns: (new_total, discount_amount)
    """
    print(f"\n--- Discount Phase ---")
    print(f"Current Subtotal: ${subtotal:.2f}")
    
    while True:
        raw_disc = input("Enter discount (e.g., '10%' for percentage, '50' for flat amount, or '0' to skip): ").strip()
        
        # Base Case: No discount
        if not raw_disc or raw_disc == '0':
            return subtotal, 0.0
            
        # Case A: Percentage-based discount
        if raw_disc.endswith('%'):
            try:
                perc = float(raw_disc[:-1]) # Strip the '%' sign and convert
                if 0 <= perc <= 100:
                    discount_amt = subtotal * (perc / 100)
                    return subtotal - discount_amt, discount_amt
            except ValueError:
                pass # Falls through to the error print at the bottom
                
        # Case B: Flat amount discount
        else:
            try:
                flat = float(raw_disc)
                if 0 <= flat <= subtotal:
                    return subtotal - flat, flat
                elif flat > subtotal:
                    print("Error: Discount cannot be greater than the subtotal")
                    continue
            except ValueError:
                pass
                
        print("Invalid input. Please enter a valid number (e.g., 20) or percentage (e.g., 15%).")


def Apply_Taxes(current_total):
    """
    Reads config.yaml. If apply_tax is true, applies the rate.
    Returns: (final_total, tax_amount, tax_rate_used)
    """
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
        # Safely drill into the dictionary, defaulting to safe values if keys are missing
        tax_info = config.get('tax_settings', {})
        apply_tax = tax_info.get('apply_tax', False)
        tax_rate = tax_info.get('tax_rate', 0.0)
        
        if apply_tax and tax_rate > 0:
            tax_amount = current_total * tax_rate
            final_total = current_total + tax_amount
            return final_total, tax_amount, tax_rate
        else:
            # Taxes are explicitly turned off in YAML, or rate is 0
            return current_total, 0.0, 0.0
            
    # GUI/App fail-safes: Never crash the app just because a config file is missing
    except FileNotFoundError:
        print("\n[System Warning] config.yaml not found. Proceeding with 0% tax.")
        return current_total, 0.0, 0.0
    except yaml.YAMLError:
        print("\n[System Warning] config.yaml is corrupted/invalid. Proceeding with 0% tax.")
        return current_total, 0.0, 0.0



def Calculate_Profit(final_cart, subtotal, discount_amount):
    # Sum up the total line costs Index 2
    total_order_cost = sum(item[2] for item in final_cart)
    
    # revenue 
    actual_revenue = subtotal - discount_amount
    
    # profit
    final_profit = actual_revenue - total_order_cost
    
    return final_profit, total_order_cost


def Package_Invoice_Data(cx_name, tier, final_cart, subtotal, discount_amount, tax_amount, grand_total, profit):
    """
    Transforms the raw checkout data into GUI-ready string formats.
    Returns a dictionary that the front-end can easily bind to visual elements.
    """
    
    # 1. Format the cart for a GUI Table Widget
    gui_table_data = []
    for item in final_cart:
        p_id, qty, line_cost, line_total , p_name = item
        unit_price = line_total / qty 
        
        # Package exactly what the GUI table needs to show, fully formatted
        gui_table_data.append(
            [str(p_id), str(qty), f"${unit_price:.2f}", f"${line_total:.2f}", p_name]
        )
        
    # 2. Package all the summary text elements
    invoice_packet = {
        "header": {
            "customer_name": cx_name,
            "tier": tier.capitalize(),
        },
        "table_data": gui_table_data, # Ready to plug directly into your GUI table element!
        "financials": {
            "subtotal": f"${subtotal:.2f}",
            "discount": f"-${discount_amount:.2f}",
            "tax": f"+${tax_amount:.2f}",
            "grand_total": f"${grand_total:.2f}",
        },
        "system_metrics": {
            "internal_profit": f"${profit:.2f}" # Keep this heavily guarded in your GUI!
        }
    }
    
    return invoice_packet


def invoice_Generation():
    #place Holder
    print()



def Phase4_Process1():
    # 1. Grab the cart from Phase 3
    final_cart = Phase3_Process1()  
    
    # 2. Get Base Subtotal
    subtotal = Calculate_Subtotal(final_cart)
    
    # 3. Apply Discounts
    discounted_total, discount_amount = Apply_Discount(subtotal)
    
    # 4. Apply Taxes (Reads from YAML)
    grand_total, tax_amount, tax_rate = Apply_Taxes(discounted_total)
    
    # 5. Calculate Profit
    profit, total_order_cost = Calculate_Profit(final_cart, subtotal, discount_amount)

    # output the BILL for managment and for client
    





def Process1():
    #place Holder
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


def update_DB():
    # This function is a placeholder for future database update logic
    print()
