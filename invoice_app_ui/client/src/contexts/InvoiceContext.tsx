import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CartItem {
  product_id: number;
  quantity: number;
}

interface InvoiceState {
  customerId: number;       // <-- NEW: 0 means new customer, >0 means existing
  customerName: string;
  tierChoice: string;
  quantityType: string;     // <-- NEW: "bulk" or "individual"
  cart: CartItem[];
  setCustomerId: (id: number) => void;
  setCustomerName: (name: string) => void;
  setTierChoice: (tier: string) => void;
  setQuantityType: (type: string) => void;
  setCart: (cart: CartItem[]) => void;
}

const InvoiceContext = createContext<InvoiceState | undefined>(undefined);

export function InvoiceProvider({ children }: { children: ReactNode }) {
  const [customerId, setCustomerId] = useState(0);
  const [customerName, setCustomerName] = useState("");
  const [tierChoice, setTierChoice] = useState("retail");
  const [quantityType, setQuantityType] = useState("individual");
  const [cart, setCart] = useState<CartItem[]>([]);

  return (
    <InvoiceContext.Provider value={{ 
      customerId, setCustomerId,
      customerName, setCustomerName, 
      tierChoice, setTierChoice, 
      quantityType, setQuantityType,
      cart, setCart 
    }}>
      {children}
    </InvoiceContext.Provider>
  );
}

export function useInvoice() {
  const context = useContext(InvoiceContext);
  if (!context) throw new Error("useInvoice must be used within an InvoiceProvider");
  return context;
}