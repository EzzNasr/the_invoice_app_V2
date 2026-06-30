# Invoice App UI: Frontend-Backend Integration Guide

This document outlines the conceptual approach for integrating the newly designed HTML/CSS frontend for the Invoice App with its existing Python backend logic. The frontend, built with React and Tailwind CSS, provides a structured pipeline for invoice creation, while the Python backend handles customer and product management, pricing logic, and invoice generation.

## 1. Frontend-Backend Communication Strategy

Given that the frontend is a static application, communication with the Python backend will primarily occur through a **RESTful API**. This approach ensures a clear separation of concerns, allowing the frontend to focus on presentation and user interaction, while the backend manages data persistence, business logic, and external integrations (like PDF generation).

To facilitate this, a thin API layer will need to be built around the existing Python functions. This layer will expose the core functionalities as HTTP endpoints that the React frontend can consume.

## 2. Conceptual API Endpoints

The following conceptual API endpoints are suggested to expose the Python backend functionalities:

| Endpoint                 | HTTP Method | Description                                                              | Python Function Mapping (Conceptual) |
| :----------------------- | :---------- | :----------------------------------------------------------------------- | :----------------------------------- |
| `/api/customers`         | `GET`       | Retrieve a list of all customers.                                        | `get_customer_list()`                |
| `/api/customers/{id}`    | `GET`       | Retrieve details for a specific customer by ID.                          | `get_customer_by_id()`               |
| `/api/customers/search`  | `GET`       | Search for a customer by name.                                           | `find_customer_by_name()`            |
| `/api/customers`         | `POST`      | Create a new customer.                                                   | `handle_new_customer()` (logic part) |
| `/api/customers/{id}/tier` | `PUT`       | Update the price tier for an existing customer.                          | `Current_Tier_logic()`               |
| `/api/products/validate` | `POST`      | Validate a list of product IDs.                                          | `Validate_Products()`                |
| `/api/invoice/calculate` | `POST`      | Calculate invoice details based on products, quantities, and customer.   | `Calculate_Profit()`, `Package_Invoice_Data()` |
| `/api/invoice/generate`  | `POST`      | Generate and save the invoice (HTML and PDF).                            | `Render_Invoice_HTML()`, `Save_And_Open_Invoice()`, `Save_Client_PDF()` |
| `/api/config/tax`        | `GET`       | Retrieve tax configuration.                                              | `get_tax_config()`                   |

## 3. Data Flow for Pipeline Steps

### Step 1: Customer Selection

*   **Frontend Action**: User selects 
an existing customer ID or enters a new customer name.
*   **Frontend Request**: 
    *   If existing: `GET /api/customers/{id}` to fetch customer details.
    *   If new: `POST /api/customers` to create a new customer. The backend should return the new customer's ID and default tier.
*   **Backend Response**: Customer details (ID, Name, Default Tier).
*   **Frontend State**: Store selected customer information (ID, Name, Tier).

### Step 2: Product Selection

*   **Frontend Action**: User inputs product IDs one by one.
*   **Frontend Request**: After user finishes inputting, `POST /api/products/validate` with a list of entered product IDs.
*   **Backend Response**: A list of validated product details (ID, Name, Retail Price, Wholesale Price, Cost) or error messages for invalid IDs.
*   **Frontend State**: Store validated product details.

### Step 3: Quantity Input

*   **Frontend Action**: User enters quantities for each validated product.
*   **Frontend Request**: `POST /api/invoice/calculate` with customer details, validated product list, and quantities.
*   **Backend Response**: Calculated invoice details, including subtotal, discount, tax, grand total, and profit (packaged as `invoice_packet`).
*   **Frontend State**: Store calculated invoice details.

### Step 4: Invoice Summary & Generation

*   **Frontend Action**: User reviews the summary and confirms invoice generation.
*   **Frontend Request**: `POST /api/invoice/generate` with the `invoice_packet` and other necessary invoice metadata (e.g., invoice number, date, business name).
*   **Backend Response**: Confirmation of invoice generation, potentially including URLs to the generated HTML and PDF files.
*   **Frontend Action**: Display success message and provide links to view/download the invoice.

## 4. Backend API Implementation Considerations

To implement the API layer in Python, you could use a lightweight web framework like **Flask** or **FastAPI**. These frameworks allow you to define routes that map to your existing Python functions, handle HTTP requests, and return JSON responses.

**Example (using Flask):**

```python
from flask import Flask, request, jsonify
import functions # Your existing functions.py

app = Flask(__name__)

@app.route("/api/customers", methods=["GET"])
def get_customers():
    customers = functions.get_customer_list()
    return jsonify(customers)

@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = functions.get_customer_by_id(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

# ... other endpoints for products, invoice calculation, generation

if __name__ == "__main__":
    app.run(debug=True)
```

## 5. Frontend Integration Details

On the frontend, you will use `fetch` or a library like `axios` to make HTTP requests to these backend endpoints. React state management (e.g., `useState`, `useContext`, or a more robust library like Redux/Zustand for larger applications) will be crucial for passing data between pipeline steps.

**Key Frontend Components for Integration:**

*   **Customer Selection**: Implement `useEffect` hooks to fetch customer lists on component mount. Use `useState` to manage input fields and selected customer data. Handle form submissions to call the appropriate backend API.
*   **Product Selection**: Manage a list of product IDs in state. On submission, send the list to the backend for validation. Display validation errors dynamically.
*   **Quantity Input**: Dynamically render input fields for each selected product. Manage quantities in state and send them to the backend for invoice calculation.
*   **Invoice Summary**: Display the `invoice_packet` data received from the backend in a user-friendly format.

## 6. Error Handling and User Feedback

Robust error handling is essential. The frontend should gracefully display error messages from the backend (e.g., "Product ID not found", "Invalid quantity"). Loading states should also be managed to provide a smooth user experience during API calls.

## 7. Next Steps

1.  **Implement the Python API Layer**: Choose a web framework (Flask/FastAPI) and create the API endpoints as outlined above, wrapping your existing `functions.py` logic.
2.  **Connect Frontend to API**: Modify the React components to make API calls and handle responses, updating the UI state accordingly.
3.  **Refine UI/UX**: Implement dynamic error messages (e.g., the red squiggle for invalid product IDs), loading indicators, and ensure smooth transitions between pipeline steps.

This guide provides a solid foundation for integrating your frontend and backend. By following these principles, you can create a robust and user-friendly Invoice App.
