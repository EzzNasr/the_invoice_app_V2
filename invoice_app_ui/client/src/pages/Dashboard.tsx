import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import { TrendingUp, Award, Users } from "lucide-react";

interface Stats {
  top_items: { name: string; qty: number }[];
  top_bills: { invoice_number: number; cx_name: string; profit: number }[];
  top_customers: { name: string; profit: number }[];
  total_profit: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/dashboard/stats")
      .then(res => res.json())
      .then(setStats)
      .catch(() => setError("Could not load dashboard stats."));
  }, []);

  if (error) return <p className="text-red-500 p-8">{error}</p>;
  if (!stats) return <p className="text-muted-foreground p-8">Loading dashboard...</p>;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-6">
      <h1 className="text-3xl font-bold flex items-center gap-2">
        <TrendingUp className="text-blue-500" /> Dashboard
      </h1>

      <div className="bg-card border rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-2">Profit Made So Far</h2>
        <p className="text-3xl font-bold text-amber-600">{stats.total_profit.toFixed(2)}</p>
      </div>

      <div className="bg-card border rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 border-b pb-2">Top 5 Most Sold Items (by Product ID)</h2>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={stats.top_items}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" label={{ value: "Product ID", position: "insideBottom", offset: -5 }} />
              <YAxis />
              <Tooltip formatter={(value: any) => [value, "Qty Sold"]} labelFormatter={(label) => `Product ID: ${label}`} />
              <Bar dataKey="qty" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 border-b pb-2 flex items-center gap-2">
            <Award size={18} className="text-amber-500" /> Top 3 Profitable Bills
          </h2>
          <div className="space-y-2">
            {stats.top_bills.map(b => (
              <div key={b.invoice_number} className="flex justify-between text-sm py-1 border-b last:border-0">
                <span>Invoice #{b.invoice_number} — {b.cx_name}</span>
                <span className="font-semibold text-amber-600">{b.profit.toFixed(2)}</span>
              </div>
            ))}
            {stats.top_bills.length === 0 && <p className="text-muted-foreground text-sm italic">No data yet.</p>}
          </div>
        </div>

        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 border-b pb-2 flex items-center gap-2">
            <Users size={18} className="text-blue-500" /> Top 3 Profitable Customers
          </h2>
          <div className="space-y-2">
            {stats.top_customers.map((cust, idx) => (
              <div key={idx} className="flex justify-between text-sm py-1 border-b last:border-0">
                <span>{cust.name}</span>
                <span className="font-semibold text-amber-600">{cust.profit.toFixed(2)}</span>
              </div>
            ))}
            {stats.top_customers.length === 0 && <p className="text-muted-foreground text-sm italic">No data yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
