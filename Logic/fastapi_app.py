import os
import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import datetime
from Logic import functions


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(title="Invoice Generation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DB dependency ---

def get_db():
    conn = sqlite3.connect(functions.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# --- Models ---

class CustomerBase(BaseModel):
    name: str
    default_tier: str

class CustomerCreate(CustomerBase):
    phone_number: Optional[str] = None

class Customer(CustomerBase):
    customer_id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    item_name: str
    retail_price: float
    wholesale_price: float
    stock_quantity: Optional[int] = None # if no stock is entered then none will be allowed to pass through 
    cost: float

class Product(ProductBase):
    product_id: int
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    product_id: int
    item_name: str
    retail_price: float
    wholesale_price: float
    cost: float
    stock_quantity: Optional[int] = None

class ProductUpdate(BaseModel):
    item_name: Optional[str] = None
    retail_price: Optional[float] = None
    wholesale_price: Optional[float] = None
    cost: Optional[float] = None
    stock_quantity: Optional[int] = None

class CartItem(BaseModel):
    product_id: int
    quantity: int

class InvoiceRequest(BaseModel):
    customer_id: int
    customer_name: str
    tier_choice: str
    order_items: List[CartItem]
    quantity_type: str
    bill_type: str
    discount_input: str = "0"
    apply_tax: bool = True
    return_invoice_number: Optional[str] = None


# --- Endpoints ---

@app.get("/customers", response_model=List[Customer])
async def get_all_customers(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    customers_data = functions.get_customer_list_pure(c)
    return [{"customer_id": cust[0], "name": cust[1], "default_tier": cust[2]} for cust in customers_data]


@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer_by_id(customer_id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    customer_data = functions.get_customer_by_id_pure(c, customer_id)
    if not customer_data:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_data[0], "name": customer_data[1], "default_tier": customer_data[2]}


@app.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    try:
        new_customer_data = functions.create_new_customer_pure(c, db, customer.name, customer.phone_number, customer.default_tier)
        db.commit()
        return {"customer_id": new_customer_data[0], "name": new_customer_data[1], "default_tier": new_customer_data[2]}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")


@app.get("/products", response_model=List[Product])
async def get_all_products(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    products_data = functions.get_all_products_pure(c)
    return [dict(product) for product in products_data]


@app.get("/products/{product_id}", response_model=Product)
async def get_product_details(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    product_data = functions.get_product_details_pure(c, product_id)
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(product_data)


@app.post("/products", response_model=Product)
async def create_product(product: ProductCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    try:
        functions.insert_new_product_pure(
            c, db, product.product_id, product.item_name,
            product.retail_price, product.wholesale_price,
            cost=product.cost, stock_quantity=product.stock_quantity
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Product ID {product.product_id} already exists.")
    return dict(functions.get_product_details_pure(c, product.product_id))


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    fields = product.dict(exclude_unset=True)
    updated = functions.update_product_pure(c, db, product_id, **fields)
    db.commit()
    return dict(updated)


@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    functions.delete_product_pure(c, db, product_id)
    db.commit()
    return {"message": f"Product {product_id} deleted."}


@app.get("/dashboard/stats")
async def get_dashboard_stats(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()

    # Top 5 most sold items by quantity
    c.execute("""
        SELECT p.Product_ID, p.item_name, SUM(od.Quantity) as total_qty
        FROM OrderDetails od
        JOIN Products p ON od.Item_ID = p.Product_ID
        GROUP BY p.Product_ID
        ORDER BY total_qty DESC
        LIMIT 5
    """)
    top_items = [{"name": str(row[0]), "qty": row[2]} for row in c.fetchall()]

    # Top 3 most profitable bills
    c.execute("""
        SELECT o.Invoice_Number, cu.Name, o.Profit
        FROM Orders o
        JOIN Customers cu ON o.Customer_ID = cu.customer_id
        WHERE o.Status != 'cancelled'
        ORDER BY o.Profit DESC
        LIMIT 3
    """)
    top_bills = [
        {"invoice_number": row[0], "cx_name": row[1], "profit": row[2]}
        for row in c.fetchall()
    ]

    # Top 3 most profitable customers
    c.execute("""
        SELECT cu.Name, SUM(o.Profit) as total_profit
        FROM Orders o
        JOIN Customers cu ON o.Customer_ID = cu.customer_id
        WHERE o.Status != 'cancelled'
        GROUP BY cu.customer_id
        ORDER BY total_profit DESC
        LIMIT 3
    """)
    top_customers = [{"name": row[0], "profit": row[1]} for row in c.fetchall()]

    # Total profit across all (non-cancelled) orders
    c.execute("SELECT SUM(Profit) FROM Orders WHERE Status != 'cancelled'")
    total_profit = c.fetchone()[0] or 0

    return {
        "top_items": top_items,
        "top_bills": top_bills,
        "top_customers": top_customers,
        "total_profit": total_profit,
    }


@app.get("/orders")
async def get_all_orders(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("""
        SELECT o.Invoice_Number, o.Date, cu.Name
        FROM Orders o
        JOIN Customers cu ON o.Customer_ID = cu.customer_id
        ORDER BY o.Invoice_Number DESC
    """)
    return [{"invoice_number": row[0], "date": row[1], "cx_name": row[2]} for row in c.fetchall()]


@app.get("/orders/{invoice_number}")
async def get_order_detail(invoice_number: int, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("""
        SELECT o.Invoice_Number, o.Date, o.Subtotal, o.Discount, o.Total, o.Profit, o.Status,
               cu.Name, cu.Default_Tier
        FROM Orders o
        JOIN Customers cu ON o.Customer_ID = cu.customer_id
        WHERE o.Invoice_Number = ?
    """, (invoice_number,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")

    c.execute("""
        SELECT od.Item_ID, p.item_name, od.Quantity, od.Price_Sold
        FROM OrderDetails od
        JOIN Products p ON od.Item_ID = p.Product_ID
        WHERE od.Invoice_Number = ?
    """, (invoice_number,))
    items = [
        {"product_id": r[0], "name": r[1], "qty": r[2], "unit_price": r[3], "line_total": r[2] * r[3]}
        for r in c.fetchall()
    ]

    return {
        "invoice_number": row[0], "date": row[1], "subtotal": row[2], "discount": row[3],
        "total": row[4], "profit": row[5], "status": row[6],
        "cx_name": row[7], "tier": row[8], "items": items,
    }


class ReturnRequest(BaseModel):
    invoice_number: int


@app.post("/return-invoice")
async def return_invoice(req: ReturnRequest, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()

    c.execute("SELECT Invoice_Number, Status FROM Orders WHERE Invoice_Number = ?", (req.invoice_number,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Invoice #{req.invoice_number} not found.")
    if row[1] == "cancelled":
        raise HTTPException(status_code=400, detail=f"Invoice #{req.invoice_number} is already cancelled.")

    track_stock = functions.get_stock_config()
    try:
        functions.Process3_cancel(req.invoice_number)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    msg = (f"Invoice #{req.invoice_number} cancelled. Stock restored."
           if track_stock else f"Invoice #{req.invoice_number} cancelled.")
    return {"message": msg}


@app.post("/generate-invoice")
async def generate_invoice(invoice_req: InvoiceRequest, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()

    # 1. Customer identification
    final_id = None
    final_name = None
    final_tier = invoice_req.tier_choice

    if invoice_req.customer_id:
        customer_data = functions.get_customer_by_id_pure(c, invoice_req.customer_id)
        if not customer_data:
            raise HTTPException(status_code=404, detail="Customer not found")
        final_id = customer_data[0]
        final_name = customer_data[1]
    elif invoice_req.customer_name:
        customer_data = functions.find_customer_by_name_pure(c, invoice_req.customer_name)
        if customer_data:
            final_id = customer_data[0]
            final_name = customer_data[1]
        else:
            final_id = 0  # new customer, real ID assigned in Process2_pure
            final_name = invoice_req.customer_name
    else:
        raise HTTPException(status_code=400, detail="Either customer_id or customer_name must be provided.")

    # 2. Validate products
    product_ids_from_request = [item.product_id for item in invoice_req.order_items]
    valid_products = functions.Validate_Products_pure(c, product_ids_from_request)
    if not valid_products:
        raise HTTPException(status_code=400, detail="One or more product IDs are invalid.")

    # 3. Build final_cart directly from the quantities the frontend already
    # resolved per item (bulk vs individual was already applied client-side
    # in QuantityInput.tsx - no need to re-branch here).
    quantities_dict = {item.product_id: item.quantity for item in invoice_req.order_items}

    final_cart = []
    for prod in valid_products:
        p_id, p_name, p_retail, p_wholesale, p_cost = prod
        qty = quantities_dict.get(p_id, 1)
        active_price = p_wholesale if final_tier == "wholesale" else p_retail
        final_cart.append((p_id, qty, p_cost * qty, active_price * qty, p_name))

    # 4. Discount / tax / profit
    subtotal_preview = sum(item[3] for item in final_cart)
    discount_pct = functions.parse_discount_input(invoice_req.discount_input, subtotal_preview)

    apply_tax, tax_rate = functions.get_tax_config()
    financials = functions.Calculate_Financials_pure(
        final_cart, discount_pct, invoice_req.apply_tax, tax_rate
    )

    invoice_date = datetime.datetime.now().strftime("%d-%m-%Y")

    invoice_packet = functions.Package_Invoice_Data(
        final_name, final_tier, final_cart,
        financials["subtotal"], financials["discount_amount"], discount_pct,
        financials["tax_amount"], financials["grand_total"], financials["profit"]
    )

    pipeline_data = {
        "customer_id": final_id,
        "cx_name": final_name,
        "cx_tier": final_tier,
        "final_cart": final_cart,
        "financials": financials,
        "invoice_date": invoice_date,
    }

    # 5. Actual bill -> write to DB, get real invoice number
    invoice_number = "MOCK"
    stock_warnings = []
    if invoice_req.bill_type == "actual":
        real_invoice_number, stock_warnings = functions.Process2_pure(db, pipeline_data)
        invoice_number = str(real_invoice_number)

    # 6. Output files
    cx_slug = final_name.replace(" ", "_")
    date_dd_mm_yy = datetime.datetime.now().strftime("%d-%m-%y")
    invoice_slug = f"{cx_slug}--invoice#{invoice_number}--{date_dd_mm_yy}"

    html_content = functions.Render_Invoice_HTML(
        invoice_packet, invoice_number, invoice_date, mode="management",
    )

    html_path, mgmt_pdf_path = functions.Save_And_Open_Invoice(
        html_content, invoice_slug, cx_name=final_name, output_dir=None
    )

    client_pdf_path = functions.Save_Client_PDF(
        invoice_packet, invoice_slug, invoice_number, invoice_date,
        cx_name=final_name, business_name="NAVY LLC", output_dir=None
    )

    return {
        "message": f"Invoice {invoice_number} generated successfully.",
        "invoice_number": invoice_number,
        "html_path": html_path,
        "management_pdf_path": mgmt_pdf_path,
        "client_pdf_path": client_pdf_path,
        "stock_warnings": stock_warnings,
    }
    

# Run: uvicorn fastapi_app:app --reload