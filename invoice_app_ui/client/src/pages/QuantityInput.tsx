import { useLocation } from "wouter";
import { useInvoice } from "../contexts/InvoiceContext";
import { Hash, ChevronRight, Layers, List } from "lucide-react";
import InvoiceStepper from "../components/InvoiceStepper";

export default function QuantityInput() {
  const [, setLocation] = useLocation();
  const { cart, setCart, quantityType, setQuantityType } = useInvoice();

  const handleBulkChange = (newQty: number) => {
    const bulkQty = newQty < 1 ? 1 : newQty;
    setCart(cart.map(item => ({ ...item, quantity: bulkQty })));
  };

  const handleIndividualChange = (index: number, newQty: number) => {
    const updatedCart = [...cart];
    updatedCart[index].quantity = newQty < 1 ? 1 : newQty;
    setCart(updatedCart);
  };

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
              value={cart[0]?.quantity || 1}
              onChange={(e) => handleBulkChange(parseInt(e.target.value) || 1)}
              className="w-32 mx-auto bg-card border rounded-md px-4 py-2 text-center text-xl font-bold outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        ) : (
          <div className="space-y-4">
            {cart.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between bg-background border p-4 rounded-md">
                <span className="font-semibold">Product ID: {item.product_id}</span>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-muted-foreground">Qty:</label>
                  <input 
                    type="number" 
                    min="1"
                    value={item.quantity}
                    onChange={(e) => handleIndividualChange(idx, parseInt(e.target.value) || 1)}
                    className="w-20 bg-background border rounded-md px-3 py-1 text-center outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            ))}
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