# Invoice App V2

A full-stack invoice and business management application built to replace spreadsheet-based workflows with a centralized, maintainable system.

Originally developed to solve a real business problem, the project evolved from a Python command-line application into a modern React + FastAPI application featuring a layered architecture, relational database design, PDF generation, inventory management, analytics, and configurable business rules.

---

# Demo

*A short demonstration of the application will be added here.*

![Demo](screenshots/demo.gif)

---

# Features

## Invoice Management

- Generate invoices in seconds
- Automatic subtotal, discount, tax, total, and profit calculations
- Generate separate Client and Management invoices
- Export invoices as PDF
- Interactive HTML invoice preview
- Historical invoice preservation
- Invoice cancellation while preserving records

---

## Customer Management

- Customer database
- Automatic customer lookup
- Retail and wholesale pricing tiers
- Create new customers during checkout
- Customer order history

---

## Inventory Management

- Product database
- Retail, wholesale, and cost tracking
- Optional inventory tracking
- Automatic stock updates
- Automatic inventory restoration after invoice cancellation

---

## Dashboard & Analytics

The integrated dashboard provides business insights directly from the database.

- Top 5 best-selling products
- Top 3 most profitable invoices
- Top 3 most profitable customers
- Order history
- Invoice lookup
- Business performance overview

---

## Configuration

Business rules are configurable through `config.yaml`.

Examples include:

- Tax rate
- Inventory tracking
- Business information
- Payment information
- PDF generation settings

No source code changes are required to modify these settings.

---

# Screenshots

## Dashboard

![Dashboard](screenshots/dashboard.png)

---

## Customer Selection

![Customer Selection](screenshots/customer-selection.png)

---

## Product Selection

![Product Selection](screenshots/product-selection.png)

---

## Quantity Input

![Quantity Input](screenshots/quantity-input.png)

---

## Invoice Summary

![Invoice Summary](screenshots/summary.png)

---

## Generated Invoice

![Generated Invoice](screenshots/invoice-preview.png)

---

## Order History

![Order History](screenshots/order-history.png)

---

# Tech Stack

## Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Wouter

## Backend

- Python
- FastAPI
- SQLite
- Jinja2
- pdfkit
- wkhtmltopdf

---

# Architecture

```
                   React + TypeScript
                           │
                    HTTP REST API
                           │
                           ▼
                    FastAPI Backend
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Business Logic      Financial Engine   PDF Generator
        │
        ▼
     SQLite Database
```

The application follows a layered architecture where the presentation layer, API, business logic, and persistence are kept separate. This makes the project easier to maintain, test, and extend.

---

# Application Flow

The following diagram summarizes the application's workflow.

![Application Flow](docs/flowchart.png)

---

# Database Schema

The application uses a normalized relational SQLite database consisting of four interconnected tables.

- Products
- Customers
- Orders
- OrderDetails

![Database Schema](docs/database-schema.png)

One important design decision was storing the exact selling price (`Price_Sold`) for every invoice line instead of referencing the current product price. This preserves historical invoices even if prices change in the future.

---

# Design Decisions

## Historical Invoice Integrity

Each order stores the exact selling price at the moment of purchase. Historical invoices therefore remain accurate even after future price updates.

---

## Layered Architecture

Business logic is separated from the FastAPI endpoints, allowing the backend logic to remain reusable and independent of the user interface.

---

## Configurable Business Rules

Tax rate, inventory tracking, business information, and PDF settings are loaded from YAML instead of being hardcoded.

---

## Soft Invoice Cancellation

Invoices are never deleted.

Cancelling an invoice:

- Restores inventory
- Removes its contribution to profit calculations
- Preserves invoice numbering
- Maintains complete historical records

---

# Invoice Generation Pipeline

Whenever an invoice is generated, the backend performs the following operations:

1. Validate customer information
2. Validate selected products
3. Build the shopping cart
4. Calculate subtotal
5. Apply discounts
6. Apply taxes
7. Calculate profit
8. Store the invoice in SQLite
9. Update inventory (optional)
10. Render the HTML invoice
11. Generate the Management PDF
12. Generate the Client PDF

---

# Project Structure

```text
the_invoice_app_V2/
│
├── Logic/
│   ├── fastapi_app.py
│   ├── functions.py
│   ├── products.py
│   ├── customers.py
│   ├── process.py
│   ├── financials.py
│   ├── Tables.py
│   ├── db.py
│   └── invoice_template.html
│
├── invoice_app_ui/
│
├── main/
│   ├── MasterDB.db
│   └── config.yaml
│
├── docs/
│   ├── flowchart.png
│   └── database-schema.png
│
├── screenshots/
│
├── Invoices/
│
├── requirements.txt
│
└── README.md
```

---

# Getting Started

## Clone the Repository

```bash
git clone https://github.com/<your_username>/Invoice_App_V2.git

cd Invoice_App_V2
```

---

## Backend Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it (Windows):

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
uvicorn Logic.fastapi_app:app --reload
```

---

## Frontend Setup

```bash
cd invoice_app_ui

npm install

npm run dev
```

---

# Future Improvements

## Business Features

- Store credit support
- Customer balance tracking
- Refunds and credit application to future invoices
- Subscription ("pay-as-you-go") model

---

## Analytics

- Revenue trends
- Monthly sales reports
- Product performance over time
- Exportable analytics

---

## Deployment

- Docker support
- PostgreSQL support
- Cloud deployment
- Automatic backups

---

## Security

- User authentication
- Role-based permissions
- Multi-user support
- Audit logging

---

# Project Goals

This project was built with four primary goals:

- Replace spreadsheet-based invoice management with a centralized system.
- Automate financial calculations while maintaining historical accuracy.
- Separate presentation, business logic, and persistence into independent layers.
- Demonstrate modern full-stack software engineering practices through a real-world application.

---

# Skills Demonstrated

- Full-stack application development
- REST API development
- React
- TypeScript
- FastAPI
- Python
- SQL database design
- SQLite
- Business logic architecture
- Financial calculations
- Inventory management
- State management
- PDF generation
- Template rendering
- Configuration management
- Software architecture
- Software refactoring
- Real-world problem solving

---

# Contact

If you have any questions, suggestions, or would like to collaborate, feel free to reach out.

**Email:** EzzNasrOne@gmail.com

---

# License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute the project under the terms of the license.
