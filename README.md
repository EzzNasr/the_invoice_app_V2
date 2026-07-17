# The Invoice App V2

**A desktop invoicing, stock, and profit-tracking system — replaces per-customer Excel files with one tool. In real commercial use today.**

[![Download](https://img.shields.io/badge/Download-Windows%20.exe-blue?style=for-the-badge&logo=windows)](../../releases/latest)
![Python](https://img.shields.io/badge/Python-FastAPI-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-Vite-3178C6?logo=typescript&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**[⬇ Download for Windows — No Install Needed](../../releases/latest)** &nbsp;·&nbsp; **[For Developers ↓](#running-from-source)**

![Demo](screenshots/demo.gif)
<sub>Full flow: pick a customer → add products → set quantities → generate — real invoice, real PDF, seconds later.</sub>

---

## Why This Exists

A real business was running every invoice through a hand-edited Excel file per customer — no history, no stock tracking, no way to answer "what did we sell most this month" without opening a dozen files. This app replaces that with one system: pick a customer, add products, get a priced, taxed, profit-calculated invoice as a PDF, with every sale recorded for good.

It started as a Python CLI tool to validate the workflow with zero UI investment, then grew into the full FastAPI + React app here — the commit history tracks that whole progression, CLI to web app, in under two weeks.

---

## Quick Start (No Setup Required)

1. Download the latest `.exe` from [**Releases**](../../releases/latest).
2. Double-click it. No Python, no Node.js, no dependencies to install.
3. Your data lives locally in a SQLite file — nothing leaves your machine.
4. when you unzip the file , you will find a folder "asstes" inside put your signature and company logo to be used instead of the current mock ones
   make sure the names of your assets are as follows : signature = signature.png , logo = logo.png
5. to exit from the app press quit from the tray icon in the taskbar.

That's the whole setup. Everything below this point is for people who want to read or modify the code.

---

## What It Does

| Feature | Screenshot |
|---|---|
| **Guided invoice creation** — pick or create a customer, add products by ID, set quantities in bulk or individually, review, generate | ![Customer Selection](screenshots/customer-selection.png) |
| **Live stock-aware warnings** — selling more than you have in stock shows a warning, never blocks the sale (real businesses sell before the count updates) | ![Quantity Input](screenshots/quantity-input.png) |
| **Two invoice documents per sale** — a management copy (with profit) and a client copy where profit is never rendered, not just hidden | ![Invoice Preview](screenshots/invoice-preview.png) |
| **Full stock management** — inline-editable product table; leave stock blank for products you don't track at all, distinct from actually having zero | ![Stock Management](screenshots/stock-management.png) |
| **Dashboard** — total profit, top sellers, most profitable bills and customers, computed live | ![Dashboard](screenshots/dashboard.png) |
| **Order history with soft cancellation** — cancelled orders are never deleted, just zeroed out of profit totals, so the record stays intact | ![Order Viewer](screenshots/order-viewer.png)<br>![Order Viewer 2](screenshots/order-viewer2.png) |

---

## Architecture

<p align="center">
  <img src="Docs/flowchart-Overall.png" alt="Overview — Bill Type Routing" width="100%">
</p>
<p align="center"><sub><b>Overview</b> — routes every bill by type (mock, actual, returned) to the process that handles it.</sub></p>

<p align="center">
  <img src="Docs/flowchart-process1.png" alt="Process 1 — Pricing & Cart" width="100%">
</p>
<p align="center"><sub><b>Process 1*</b> — customer resolution, price tier selection, cart building, discount/tax/profit calculation.</sub></p>

<p align="center">
  <img src="Docs/flowchart-process2.png" alt="Process 2 — Database Write & Document Generation" width="100%">
</p>
<p align="center"><sub><b>Process 2*</b> — commits the sale to the database (customer, order, line items, stock) and generates both invoice documents.</sub></p>

<p align="center">
  <img src="Docs/flowchart-process3.png" alt="Process 3 — Returns & Cancellation" width="100%">
</p>
<p align="center"><sub><b>Process 3*</b> — cancels an invoice, restores stock, and zeroes its profit contribution without ever deleting the record.</sub></p>

Every piece of business logic exists in two forms: a `_pure` version that FastAPI calls (takes an explicit DB connection, raises exceptions, no blocking input), and the original CLI version it was refactored from. Neither reimplements the other — they share the same underlying data layer.

**[Database schema (Rev. 2, corrected) →](Docs/Database_Schema_v2.pdf)** &nbsp;·&nbsp; **[Full pipeline breakdown, text/Mermaid reference, and every endpoint →](Docs/architecture.md)**

---

## Interesting Engineering Decisions

**NULL vs. zero stock.** Early on, "0 units in stock" and "we don't track this product's stock" were indistinguishable — both were just `0`. Now `stock_quantity` is `NULL` for untracked products and `0` for genuinely empty. Every warning, dashboard stat, and low-stock check reads this distinction, and the frontend's stock table shows untracked fields as blank, not zero.

**Soft failures over hard blocks.** Overselling triggers a warning, not a rejection — real sales sometimes get entered before stock counts catch up, and stopping an employee mid-sale over a data-entry race condition is worse than letting them proceed with eyes open.

**Client PDFs never contain profit — structurally, not visually.** The client-facing invoice is a separate server-side render where the profit row is wrapped in a template conditional, not hidden with CSS. There's no version of the client PDF where profit exists in the file at all.

**Soft cancellation.** Returned/cancelled invoices are never deleted. The order stays in the database permanently, with its profit zeroed out of every dashboard total — the historical record is preserved even when the sale itself is reversed.

**Migrating real historical invoices, not just the price catalog.** The data-migration script doesn't just import products — it ingests old per-customer Excel invoice files and determines whether each one was a retail or wholesale sale by comparing recorded line values against both price tiers across the first several rows and taking whichever tier matches more often. No stored "invoice type" field existed in the old files; this recovers it after the fact.

---

## Known Limitations / Roadmap

- **No authentication.** Fine for the current single-machine desktop use case; flagged for whenever a multi-user or hosted version happens.
- **No automated tests yet.** Test tooling is in place (`pytest`, `ruff`); a real suite is next.

---

## Running From Source

For anyone who wants to read, modify, or build the app themselves rather than just run the `.exe`.

**Backend**
```bash
pip install -r requirments.txt
cd main
python main.py
```

**Frontend**
```bash
cd invoice_app_ui
npm install
npm run dev
```

The frontend expects the backend running on `localhost:8000`.

---

## Tech Stack

- **Backend:** Python, FastAPI, SQLite (stdlib `sqlite3`, no ORM), Jinja2, Playwright (headless Chromium for PDF generation), PyYAML
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, wouter, recharts
- **Packaging:** PyInstaller (standalone Windows executable, no runtime dependencies)

---

## License

MIT — see [LICENSE](LICENSE).
