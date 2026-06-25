import sqlite3 
conn = sqlite3.connect('MasterDB.db')
c = conn.cursor()

# profit is total - cost price 
def Process1(name):

    print()

def calculate_profit():
    
    print()

def bill_type():
    # 1 = mock , 2= Actual , 3 = Return 
    
    name = input(f"please enter Cx name: ")

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