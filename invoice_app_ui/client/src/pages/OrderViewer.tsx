import { useEffect, useState } from "react";
import { useParams } from "wouter";
import { FileText } from "lucide-react";

interface OrderItem {
  product_id: number;
  name: string;
  qty: number;
  unit_price: number;
  line_total: number;
}

interface OrderDetail {
  invoice_number: number;
  date: string;
  cx_name: string;
  tier: string;
  subtotal: number;
  discount: number;
  total: number;
  profit: number;
  status: string;
  items: OrderItem[];
}

export default function OrderViewer() {
  const { id } = useParams();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    fetch(`http://localhost:8000/orders/${id}`)
      .then(res => {
        if (!res.ok) throw new Error("Order not found");
        return res.json();
      })
      .then(setOrder)
      .catch(() => setError("Could not load this order."));
  }, [id]);

  if (error) return <p className="text-red-500">{error}</p>;
  if (!order) return <p className="text-muted-foreground">Loading order #{id}...</p>;

  return (
    <div className="max-w-3xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <FileText className="text-blue-500" /> Invoice #{order.invoice_number}
      </h1>

      <div className="bg-card border rounded-xl p-6 shadow-sm space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-muted-foreground">Customer:</span> <span className="font-semibold">{order.cx_name}</span></div>
          <div><span className="text-muted-foreground">Date:</span> <span className="font-semibold">{order.date}</span></div>
          <div><span className="text-muted-foreground">Tier:</span> <span className="font-semibold capitalize">{order.tier}</span></div>
          <div><span className="text-muted-foreground">Status:</span> <span className="font-semibold capitalize">{order.status}</span></div>
        </div>

        <table className="w-full text-sm mt-4">
          <thead>
            <tr className="text-left text-muted-foreground border-b">
              <th className="py-2">Product</th>
              <th className="py-2">Qty</th>
              <th className="py-2 text-right">Unit Price</th>
              <th className="py-2 text-right">Line Total</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map((it, idx) => (
              <tr key={idx} className="border-b last:border-0">
                <td className="py-2">{it.name}</td>
                <td className="py-2">{it.qty}</td>
                <td className="py-2 text-right">{it.unit_price.toFixed(2)}</td>
                <td className="py-2 text-right">{it.line_total.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="border-t pt-4 space-y-1 text-sm ml-auto max-w-xs">
          <div className="flex justify-between"><span>Subtotal</span><span>{order.subtotal.toFixed(2)}</span></div>
          <div className="flex justify-between"><span>Discount</span><span>-{order.discount.toFixed(2)}</span></div>
          <div className="flex justify-between font-bold text-base border-t pt-2"><span>Total</span><span>{order.total.toFixed(2)}</span></div>
          <div className="flex justify-between text-amber-600"><span>Profit</span><span>{order.profit.toFixed(2)}</span></div>
        </div>
      </div>
    </div>
  );
}
