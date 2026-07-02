import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useInvoice } from "../contexts/InvoiceContext";
import { Hash, ChevronRight, Layers, List, AlertTriangle } from "lucide-react";
import InvoiceStepper from "../components/InvoiceStepper";

interface ProductStock {
  product_id: number;
  item_name: string;
  stock_quantity: number | null;
}

export default function QuantityInput() {
  const [, setLocation] = useLocation();
  const { cart, setCart, quantityType, setQuantityType } = useInvoice();

  const [stockMap, setStockMap] = useState<Record<number, ProductStock>>({});

  useEffect(() => {
    fetch("http://localhost:8000/products")
      .then(res => res.json())
      .then((data: ProductStock[]) => {
        const map: Record<number, ProductStock> = {};
        data.forEach(p => { map[p.product_id] = p; });
        setStockMap(map);
      })
      .catch(err => console.error("Could not fetch product stock:", err));
  }, []);

  // Soft check only - null/undefined stock means "untracked", never flagged as insufficient.
  const isOverselling = (productId: number, qty: number) => {
    const stock = stockMap[productId]?.stock_quantity;
    return stock !== null && stock !== undefined && qty > stock;
  };

  const handleBulkChange = (newQty: number) => {
    const bulkQty = newQty < 1 ? 1 : newQty;
    setCart(cart.map(item => ({ ...item, quantity: bulkQty })));
  };

  const handleIndividualChange = (index: number, newQty: number) => {
    const updatedCart = [...cart];
    updatedCart[index].quantity = newQty < 1 ? 1 : newQty;
    setCart(updatedCart);
  };

  const bulkQty = cart[0]?.quantity || 1;
  const bulkOversellItems = cart.filter(item => isOverselling(item.product_id, bulkQty));

  return (
    <>
      <InvoiceStepper />
      <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Hash className="text-blue-500" /> Set Quantities
      </h1>

      <div className="bg-card border rounded-xl p-6 shadow-sm space-y-6">
        {/* Bulk vs Individual Toggle */}
        <div className="flex bg-background border rounded-lg p-1">
          <button
            type="button"
            onClick={() => setQuantityType("bulk")}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md font-medium transition-colors ${quantityType === "bulk" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:bg-muted"}`}
          >
            <Layers size={18} /> Bulk Quantity
          </button>
          <button
            type="button"
            onClick={() => setQuantityType("individual")}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md font-medium transition-colors ${quantityType === "individual" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:bg-muted"}`}
          >
            <List size={18} /> Individual
          </button>
        </div>

        {quantityType === "bulk" ? (
          <div className="bg-background border rounded-lg p-6 text-center space-y-4">
            <h3 className="font-semibold text-lg">Apply to All Items</h3>
            <p className="text-muted-foreground text-sm">This quantity will be applied to every product in your cart.</p>
            <input
              type="number"
              min="1"
              value={bulkQty}
              onChange={(e) => handleBulkChange(parseInt(e.target.value) || 1)}
              className="w-32 mx-auto bg-card border rounded-md px-4 py-2 text-center text-xl font-bold outline-none focus:ring-2 focus:ring-blue-500"
            />
            {bulkOversellItems.length > 0 && (
              <div className="text-left bg-amber-500/10 text-amber-600 border border-amber-500/20 rounded-md p-3 text-sm flex gap-2">
                <AlertTriangle size={18} className="flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">This quantity exceeds current stock for:</p>
                  <ul className="mt-1 space-y-0.5">
                    {bulkOversellItems.map(item => (
                      <li key={item.product_id}>
                        {stockMap[item.product_id]?.item_name ?? `Product ${item.product_id}`}
                        {" "}(only {stockMap[item.product_id]?.stock_quantity} in stock)
                      </li>
                    ))}
                  </ul>
                  <p className="mt-1 opacity-80">You can still proceed — this is a warning, not a block.</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {cart.map((item, idx) => {
              const oversell = isOverselling(item.product_id, item.quantity);
              return (
                <div key={idx} className="bg-background border rounded-md p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Product ID: {item.product_id}</span>
                    <div className="flex items-center gap-3">
                      <label className="text-sm text-muted-foreground">Qty:</label>
                      <input
                        type="number"
                        min="1"
                        value={item.quantity}
                        onChange={(e) => handleIndividualChange(idx, parseInt(e.target.value) || 1)}
                        className={`w-20 bg-background border rounded-md px-3 py-1 text-center outline-none focus:ring-2 ${
                          oversell ? "border-amber-500 focus:ring-amber-500" : "focus:ring-blue-500"
                        }`}
                      />
                    </div>
                  </div>
                  {oversell && (
                    <div className="text-amber-600 text-xs flex items-center gap-1">
                      <AlertTriangle size={14} />
                      Only {stockMap[item.product_id]?.stock_quantity} in stock — you can still proceed.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        <button
          onClick={() => setLocation("/summary")}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-md flex justify-center items-center gap-2"
        >
          Next: Review Summary <ChevronRight size={18} />
        </button>
      </div>
      </div>
    </>
  );
}