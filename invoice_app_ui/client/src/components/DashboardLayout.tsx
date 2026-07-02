import { useState, useEffect } from "react";
import { useLocation, Link } from "wouter";
import { FileText, LayoutDashboard, ReceiptText, Boxes } from "lucide-react";

interface OrderListItem {
  invoice_number: number | string;
  date: string;
  cx_name: string;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [, setLocation] = useLocation();
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [selectedOrder, setSelectedOrder] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/orders")
      .then(res => res.json())
      .then(data => setOrders(data))
      .catch(err => console.error("Could not fetch orders:", err));
  }, []);

  const handleOrderSelect = (invoiceNumber: string) => {
    setSelectedOrder(invoiceNumber);
    if (invoiceNumber) setLocation(`/orders/${invoiceNumber}`);
  };

  
  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r bg-card flex flex-col p-4 gap-6 h-screen sticky top-0">
        <div className="text-lg font-bold px-2">Invoice App</div>

        <Link
          href="/"
          className="flex items-center gap-2 px-2 py-2 rounded-md text-sm font-medium hover:bg-muted"
        >
          <FileText size={16} /> New Invoice
        </Link>

        {/* Orders section */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-2 text-xs font-semibold uppercase text-muted-foreground">
            <ReceiptText size={14} /> Orders
          </div>
          <select
            value={selectedOrder}
            onChange={(e) => handleOrderSelect(e.target.value)}
            className="w-full bg-background border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- View an order --</option>
            {orders.map(o => (
              <option key={o.invoice_number} value={o.invoice_number}>
                #{o.invoice_number} - {o.date} - {o.cx_name}
              </option>
            ))}
          </select>
        </div>

        {/* Dashboard placeholder - not populated yet */}
        <div className="mt-auto space-y-1 pb-4">
          <Link
            href="/stock"
            className="flex items-center gap-2 px-2 py-2 rounded-md text-sm font-medium hover:bg-muted"
          >
            <Boxes size={16} /> Stock Management
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-2 py-2 rounded-md text-sm font-medium hover:bg-muted"
          >
            <LayoutDashboard size={16} /> Dashboard
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}