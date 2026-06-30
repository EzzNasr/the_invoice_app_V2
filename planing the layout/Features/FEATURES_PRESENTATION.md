# The Invoice App V2
### Your business, finally under control.

---

## The Problem It Solves

Running a business on scattered Excel sheets means lost invoices, wrong prices sent to clients, no idea what your actual profit was last month, and zero history of what any customer ever bought. Every bill is a manual job. Every mistake costs you money.

**The Invoice App replaces all of that with one system.**

---

## What It Does

### One place for everything
Every customer, every product, every invoice — stored in a single database. No more hunting through folders. No more duplicate files. No more "which Excel was the final one?"

### Bills in seconds, not minutes
Search a customer by name or ID, add products, set quantities, and the bill is done. The app calculates subtotal, discount, tax, and profit automatically — no manual arithmetic, no rounding errors.

### Two versions of every invoice, automatically
Every bill generates two outputs:
- A **client copy** — clean, professional, nothing they shouldn't see.
- A **management copy** — same bill, but includes your profit margin for that order.

Both are saved as PDFs the moment you hit Generate. The management copy opens instantly in your browser.

### You always know your profit
Every invoice records the exact profit you made on that order — not an estimate, the real number, calculated from your actual cost prices. At any point you can look up any past order and see what you made on it.

### Wholesale and retail, handled automatically
Customers have a default pricing tier. The app applies the right prices automatically, and you can override the tier for any individual bill without changing the customer's default.

### Discounts and tax, your way
Apply a discount as a percentage or a flat amount. Tax rate is set once in a config file and applied automatically — or toggled off per bill if needed. Everything recalculates instantly as you make changes.

### A full history of every order
The orders sidebar lets you pull up any past invoice immediately — customer name, date, itemized list, totals, and profit — without searching through files.

### Returns handled cleanly
Need to reverse an order? Enter the invoice number, confirm, and the system cancels the order and restores stock. The original invoice record is preserved — nothing is deleted, the history stays intact.

### Stock tracking (optional)
Turn stock tracking on or off in settings. When enabled, stock levels update automatically when an actual bill is committed, and the management invoice shows how many units remain for each item sold.

---

## Who It's For

Any small business that sells physical products to a mix of wholesale and retail customers, issues invoices regularly, and wants to know their actual profit without doing it manually.

---

## The Outputs You Get

For every invoice generated:

| File | Who sees it | What's in it |
|---|---|---|
| Client PDF | Customer | Items, quantities, prices, discount, tax, total |
| Management PDF | Internal | Same as above + profit margin |
| Management HTML | Internal | Interactive — toggle between client/management view, print directly from browser |

All three files are saved automatically in an organized folder structure:
```
Invoices/
  └── Customer Name/
        └── Customer--invoice#42--29-06-26/
              ├── invoice.html        (management, interactive)
              ├── invoice-MGMT.pdf    (management copy)
              └── invoice-CLIENT.pdf  (client copy)
```

---

## In Short

Stop doing your invoices by hand. Stop guessing your profit. Stop losing your history. The Invoice App gives you a real billing system — fast, accurate, and built around how your business actually works.
