# The Invoice App V2 — Technical Reference
### Architecture, stack, and implementation detail

---

## Stack

| Layer | Technology |
|---|---|
| Backend API | Python · FastAPI · Uvicorn |
| Database | SQLite (`MasterDB.db`) via `sqlite3` stdlib |
| Business logic | Pure Python (`functions.py`) |
| Template engine | Jinja2 |
| PDF generation | pdfkit + wkhtmltopdf |
| Frontend | React 18 · TypeScript · Vite |
| Routing | wouter |
| Styling | Tailwind CSS + shadcn/ui |
| State | React Context API (`InvoiceContext`) |
| Inter-process | HTTP REST (FastAPI ↔ React via fetch) |
| Config | YAML (`config.yaml`) parsed with PyYAML |

---

## Project Structure

```
the_invoice_app_V2/
├── Logic/
│   ├── functions.py            # all business logic, pure functions
│   ├── fastapi_app.py          # REST API layer, no logic of its own
│   ├── Tables.py               # schema creation (CREATE TABLE IF NOT EXISTS)
│   ├── Tablefunctions.py       # CLI debug helpers (ViewTable, ClearTable, etc.)
│   ├── dataMigration.py        # one-off Excel→DB migration
│   ├── invoice_template.html   # Jinja2 HTML invoice template
│   └── config.yaml             # tax, stock, business info, PDF settings
├── invoice_app_ui/             # Vite/React frontend
│   └── src/
│       ├── pages/              # CustomerSelection, ProductSelection,
│       │                       # QuantityInput, Summary, OrderViewer, Dashboard
│       ├── contexts/
│       │   └── InvoiceContext.tsx   # shared invoice state across pages
│       ├── components/
│       │   └── DashboardLayout.tsx  # sidebar shell with orders dropdown
│       └── App.tsx             # wouter route table
└── Invoices/
    └── <cx_name>/
        └── <invoice_slug>/
            ├── invoice.html
            ├── invoice-MGMT.pdf
            └── invoice-CLIENT.pdf
```

---

## Database Schema

Four tables. SQLite, no ORM.

### Products
```sql
CREATE TABLE Products (
    Product_ID      INTEGER PRIMARY KEY,
    item_name       TEXT,
    description     TEXT,
    Retail_Price    REAL,
    Wholesale_Price REAL,
    stock_quantity  INTEGER,
    Cost            REAL DEFAULT 0.0
)
```

### Customers
```sql
CREATE TABLE Customers (
    customer_id  INTEGER PRIMARY KEY,
    Name         TEXT NOT NULL,
    Phone_Number TEXT,
    Default_Tier TEXT      -- "retail" | "wholesale"
)
```

### Orders
```sql
CREATE TABLE Orders (
    Invoice_Number INTEGER PRIMARY KEY AUTOINCREMENT,
    Customer_ID    INTEGER NOT NULL,
    Date           TEXT NOT NULL,
    Subtotal       REAL NOT NULL,
    Discount       REAL NOT NULL,
    Total          REAL NOT NULL,
    Profit         REAL NOT NULL,
    Status         TEXT NOT NULL,   -- "active" | "cancelled"
    FOREIGN KEY (Customer_ID) REFERENCES Customers(customer_id)
)
```

### OrderDetails
```sql
CREATE TABLE OrderDetails (
    Invoice_Number INTEGER NOT NULL,
    Item_ID        INTEGER NOT NULL,
    Quantity       INTEGER NOT NULL,
    Price_Sold     REAL NOT NULL,   -- locked at time of sale
    FOREIGN KEY (Invoice_Number) REFERENCES Orders(Invoice_Number),
    FOREIGN KEY (Item_ID) REFERENCES Products(Product_ID)
)
```

`Price_Sold` is intentionally denormalized — it locks the price at the moment of the transaction so historical invoices are unaffected by future price changes.

---

## API Endpoints (FastAPI)

| Method | Path | Purpose |
|---|---|---|
| GET | `/customers` | Full customer list |
| GET | `/customers/{id}` | Single customer by ID |
| POST | `/customers` | Create new customer |
| GET | `/products` | Full product list |
| GET | `/products/{id}` | Single product by ID |
| GET | `/orders` | Order list (invoice#, date, cx name) for sidebar |
| GET | `/orders/{id}` | Full order detail + line items JOIN |
| POST | `/generate-invoice` | Full invoice pipeline (see below) |

CORS is open (`allow_origins=["*"]`) for local development. DB dependency uses FastAPI's `Depends(get_db)` pattern — one connection per request, closed in `finally`.

---

## The Invoice Generation Pipeline

`POST /generate-invoice` receives an `InvoiceRequest` and runs the following in sequence, all within one request:

```
1. Customer resolution
   ├── customer_id > 0  →  get_customer_by_id_pure(c, id)
   ├── customer_name provided, found  →  find_customer_by_name_pure(c, name)
   └── customer_name provided, not found  →  final_id = 0 (new, inserted in step 5)

2. Product validation
   └── Validate_Products_pure(c, product_ids)
       └── SELECT Product_ID, item_name, Retail_Price, Wholesale_Price, Cost
           FROM Products WHERE Product_ID IN (?, ?, ...)

3. Cart building (server-side)
   └── For each valid_product:
       active_price = Wholesale_Price if tier=="wholesale" else Retail_Price
       cart_row = (p_id, qty, cost*qty, active_price*qty, p_name)
       (quantities already resolved client-side in QuantityInput.tsx)

4. Financial calculations
   ├── parse_discount_input(raw_string, subtotal)
   │   └── handles "10%" → 10.0  |  "50" → flat→equivalent pct
   ├── Calculate_Financials_pure(final_cart, discount_pct, apply_tax, tax_rate)
   │   ├── subtotal    = sum(item[3] for item in cart)   # index 3 = line price
   │   ├── discount    = subtotal × (discount_pct / 100)
   │   ├── after_disc  = subtotal - discount
   │   ├── tax         = after_disc × tax_rate  (if apply_tax)
   │   ├── grand_total = after_disc + tax
   │   └── profit      = grand_total - sum(item[2] for item in cart)
   │                                           # index 2 = line cost
   └── Package_Invoice_Data(...)
       └── builds structured dict consumed by Jinja2 template

5. DB write (Actual Bills only)
   └── Process2_pure(db, pipeline_data)
       ├── INSERT new customer if final_id == 0, gets lastrowid
       ├── INSERT INTO Orders → gets real Invoice_Number via lastrowid
       ├── INSERT INTO OrderDetails for each cart line
       └── UPDATE Products SET stock_quantity = stock_quantity - qty
           (only if track_stock: true in config.yaml)

6. Slug + output paths
   └── "{cx_name}--invoice#{number}--{dd-mm-yy}"
       └── Invoices/{cx_name}/{slug}/

7. HTML render
   └── Render_Invoice_HTML(invoice_packet, invoice_number, invoice_date, mode)
       └── Jinja2 Template.render(...)
           ├── {% for row in table_rows %}  → line items loop
           ├── {% if mode == "management" or allow_toggle %}  → profit row
           └── @media print { .mode-banner, .controls { display: none } }

8. File save + auto-open
   ├── Save_And_Open_Invoice()  →  writes .html, renders MGMT .pdf via pdfkit,
   │                               opens HTML in default browser via webbrowser.open()
   └── Save_Client_PDF()        →  re-renders template with mode="client"
                                   (profit row stripped at Jinja2 level, not CSS),
                                   saves CLIENT .pdf

9. Return JSON
   └── { invoice_number, html_path, management_pdf_path, client_pdf_path }
```

---

## GUI-Readiness Pattern (functions.py)

Every function with side effects is split into two layers:

```python
# Pure logic - no input(), no print(), raises ValueError on bad input.
# This is what the FastAPI endpoint (and future GUI) calls directly.
def get_customer_by_id_pure(c, cx_id):
    c.execute("SELECT customer_id, Name, Default_Tier FROM Customers WHERE customer_id = ?", (cx_id,))
    result = c.fetchone()
    return result if result else None

# CLI wrapper - loops on input(), catches ValueError, re-prompts.
# Unchanged behavior from original CLI; delegates to the pure function.
def handle_existing_customer():
    present_CX_List()
    while True:
        c_input = input("Choose customer: ").strip()
        try:
            c_id = int(c_input)
            found = get_customer_by_id_pure(c, c_id)
            if found: return found
            print(f"{c_id} not found.")
        except ValueError:
            print("Enter a valid number.")
```

`ValueError` is raised by logic functions (not looped internally) because a GUI reacts to it differently — it shows a validation state and waits for the next event, rather than blocking in a `while True`.

---

## Invoice Template Architecture

`invoice_template.html` is a standalone Jinja2 template, not a React component.

**Toggle mode** (current): one file rendered with `allow_toggle=True`. JavaScript on the page toggles profit row visibility and banner text between "MANAGEMENT COPY" and "CLIENT COPY". Profit is present in the DOM either way — safe for internal use/printing, not for emailing to clients.

**Print isolation** via CSS:
```css
@media print {
  .controls, .mode-banner { display: none !important; }
  body { background: white; padding: 0; }
  .sheet { border: none; max-width: none; }
}
```
Confirmed working: banner and toggle buttons are absent from pdfkit-rendered PDF output.

**Client PDF** is rendered server-side with `mode="client"`, `allow_toggle=False`. Jinja2's `{% if %}` means the profit markup is never emitted into that file at all — not just hidden.

---

## Frontend State Flow

```
InvoiceContext (React Context)
  ├── customerId    (int, 0 = new)
  ├── customerName  (str)
  ├── tierChoice    (str, "retail"|"wholesale")
  ├── quantityType  (str, "bulk"|"individual")
  └── cart          (CartItem[]: {product_id, quantity}[])

Page flow (wouter routes):
  /  →  CustomerSelection  →  /products
                               └── ProductSelection  →  /quantities
                                                        └── QuantityInput  →  /summary
                                                                              └── Summary → POST /generate-invoice

Sidebar (DashboardLayout):
  GET /orders  →  dropdown list
  select  →  navigate to /orders/:id
             └── OrderViewer  →  GET /orders/{id}
```

---

## Config (config.yaml)

```yaml
tax_settings:
  apply_tax: true
  tax_rate: 0.14

stock_settings:
  track_stock: true        # if false, no stock reads/writes anywhere

business_info:
  name: "The Invoice App"
  logo_path: "assets/logo.png"
  signature_path: "assets/signature.png"

payment_info:
  bank_name: "Your Bank"
  account_name: "Your Name"
  account_number: "0000 0000 0000"

invoice_settings:
  due_in_days: 30

pdf_settings:
  wkhtmltopdf_path: null   # set to full .exe path if not on PATH (Windows)
```

All settings are read at runtime, not import time — changing the file takes effect on the next request without restarting the server.

---

## Data Migration (`dataMigration.py`)

One-off script that ingested legacy per-customer Excel invoice files into `MasterDB.db`.

Key implementation details:
- **Tier detection via "mathematical lie detector"**: for each Excel row, computes `qty × retail_price` and `qty × wholesale_price` and compares both against the recorded line value. Whichever matches within ±1.0 EGP wins the vote. Run across the first 15 rows; majority wins.
- **Price catalog lookup**: loads `Office_Sanatized.xlsx` first; every product's true `cost`, `wholesale`, `retail` sourced from there rather than inferred from invoice columns. Falls back to invoice column data + a `cost = wholesale × 0.90` estimate only if a product ID is missing from the catalog.
- **Arabic column matching**: column detection uses partial string matching against Arabic header names (`جملة`, `مكتب`, `عدد`, `قيمة`, `نسبة الخصم`) to handle encoding variance across files.

---

## Known Issues / Deferred Work

| Item | Status |
|---|---|
| FK clauses on Orders/OrderDetails reference old column names (`cx_ID`, `Item_ID`) | Dormant — SQLite doesn't enforce FK targets at CREATE time; breaks if `PRAGMA foreign_keys = ON` |
| `process3` (return/cancel bill) | Not yet implemented in `functions.py` |
| Dashboard page | Route exists, page is an empty placeholder |
| `business_name` in `config.yaml` not yet wired into `Render_Invoice_HTML` call in `fastapi_app.py` | Hardcoded to `"NAVY LLC"` in the `Save_Client_PDF` call |
| Customer names stored lowercase (`.strip().lower()` in `handle_new_customer`) | Prints lowercase on invoice; title-casing not yet applied at render time |
