# Architecture Deep Dive

> **Note:** The primary visuals for this project are the hand-designed flowchart (`Docs/flowchart.png`) and database schema doc (`Docs/Database_Schema_v2.pdf`), linked from the main README. The diagrams below are a secondary, text-searchable reference  for reading inline without an image viewer, but not the polished versions.
>
> **I
## Database Schema

```mermaid
erDiagram
    Products {
        int Product_ID PK
        text item_name
        text description
        real Retail_Price
        real Wholesale_Price
        int stock_quantity "NULL = untracked, not zero"
        real Cost
    }
    Customers {
        int customer_id PK
        text Name
        text Phone_Number
        text Default_Tier "retail or wholesale"
    }
    Orders {
        int Invoice_Number PK
        int Customer_ID FK
        text Date
        real Subtotal
        real Discount
        real Total
        real Profit
        text Status "active or cancelled"
    }
    OrderDetails {
        int Invoice_Number FK
        int Item_ID FK
        int Quantity
        real Price_Sold "locked at time of sale"
    }
    Customers ||--o{ Orders : places
    Orders ||--o{ OrderDetails : contains
    Products ||--o{ OrderDetails : "sold as"
```

`Price_Sold` is deliberately denormalized — it's a snapshot of the price at the moment of sale, not a live reference to the product's current price. This keeps historical invoices accurate even after prices change later.

## The Invoice Generation Pipeline

```mermaid
sequenceDiagram
    participant U as User (React)
    participant A as FastAPI
    participant D as SQLite

    U->>A: POST /generate-invoice
    A->>D: Resolve customer (existing / new / by name)
    A->>D: Validate all product IDs in one query
    A->>A: Build cart server-side (price from DB, not client)
    A->>A: Parse discount, calculate tax + profit
    alt bill_type == actual
        A->>D: Insert customer (if new), Orders row, OrderDetails rows
        A->>D: Decrement stock (soft warning if it goes negative)
    else bill_type == mock
        Note over A,D: No DB write — invoice number returned as "MOCK"
    end
    A->>A: Render management HTML (Jinja2, profit included)
    A->>A: Render client HTML (profit never emitted — template conditional)
    A->>A: Convert both to PDF via Playwright (headless Chromium)
    A-->>U: Invoice number, file paths, stock warnings (if any)
```

## Every Endpoint

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/customers` | List all customers |
| `GET` | `/customers/{id}` | Single customer |
| `POST` | `/customers` | Create customer |
| `GET` | `/products` | List all products |
| `GET` | `/products/{id}` | Single product |
| `POST` | `/products` | Create product |
| `PUT` | `/products/{id}` | Partial update — can explicitly null out stock to mark untracked |
| `DELETE` | `/products/{id}` | Delete — blocked if the product appears in any historical order |
| `GET` | `/dashboard/stats` | Top sellers, most profitable bills/customers, total profit |
| `GET` | `/orders` | Order list (for the sidebar picker) |
| `GET` | `/orders/{invoice_number}` | Full order detail with line items |
| `POST` | `/return-invoice` | Cancel an order — soft delete, profit zeroed, record kept |
| `POST` | `/generate-invoice` | The full pipeline above |

## The CLI / Pure Split

Every logic module (`customers.py`, `products.py`, `cart.py`, `financials.py`, `process.py`) contains two versions of its core functions:

- **CLI version** — the original terminal-tool function, uses `input()` to prompt and loop on bad input, prints directly to the console.
- **`_pure` version** — takes an explicit cursor/connection argument, raises exceptions instead of looping, returns data instead of printing. This is what FastAPI calls.

`functions.py` itself contains no logic — it's a re-export barrel so nothing importing from the original monolithic file broke when it was split into these modules.

## Return / Cancellation

Cancelling an order:
1. Sets `Orders.Status = 'cancelled'`
2. Zeroes `Orders.Profit` — every dashboard aggregate explicitly excludes cancelled orders from profit totals
3. Restores stock for each line item (if stock tracking is on)
4. **Never deletes the order, its line items, or its invoice number** — the historical record stays intact permanently