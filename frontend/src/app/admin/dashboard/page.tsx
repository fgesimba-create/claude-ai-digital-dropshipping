"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  TrendingUp, DollarSign, ShoppingBag, Package, Shield,
  RefreshCw, Zap, AlertTriangle, CheckCircle, Clock, Play
} from "lucide-react";

interface DashboardData {
  today: { revenue: number; profit: number; orders: number; profit_margin: number };
  all_time: { revenue: number; profit: number; orders: number; active_products: number };
  recent_orders: { order_number: string; customer: string; total: number; status: string; created_at: string }[];
  latest_ai_report: { date: string; executive_summary: string; recommendations: unknown[] } | null;
  security_status: { last_scan: string; risk_level: string; findings_count: number } | null;
}

function StatCard({ icon: Icon, label, value, sub, color = "blue" }: {
  icon: React.ElementType; label: string; value: string; sub?: string; color?: string;
}) {
  const colors: Record<string, string> = {
    blue: "bg-blue-900/40 text-blue-400",
    green: "bg-green-900/40 text-green-400",
    purple: "bg-purple-900/40 text-purple-400",
    orange: "bg-orange-900/40 text-orange-400",
  };
  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-600 mt-1">{sub}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  pending: "text-yellow-400",
  payment_confirmed: "text-blue-400",
  submitted_to_supplier: "text-purple-400",
  shipped: "text-green-400",
  delivered: "text-green-600",
  cancelled: "text-red-400",
};

const RISK_COLORS: Record<string, string> = {
  low: "text-green-400",
  medium: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

export default function AdminDashboard() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) { router.push("/admin"); return; }
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/admin/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401) { router.push("/admin"); return; }
      setData(await res.json());
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  async function triggerTask(task: string) {
    const token = localStorage.getItem("admin_token");
    setTriggering(task);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${apiUrl}/api/admin/automation/trigger/${task}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } finally {
      setTriggering(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Zap className="w-12 h-12 text-brand-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const automationTasks = [
    { id: "product_discovery", label: "Discover Products", icon: TrendingUp },
    { id: "price_update", label: "Optimize Prices", icon: DollarSign },
    { id: "inventory_sync", label: "Sync Inventory", icon: Package },
    { id: "security_scan", label: "Security Scan", icon: Shield },
    { id: "daily_report", label: "Generate Report", icon: RefreshCw },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">TechFlow Command Center</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered — fully autonomous operation</p>
        </div>
        <button onClick={fetchDashboard} className="btn-outline flex items-center gap-2 text-sm py-2">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Today's metrics */}
      <div className="mb-2">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Today</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={DollarSign} label="Revenue" value={`$${data.today.revenue.toFixed(2)}`} color="green" />
          <StatCard icon={TrendingUp} label="Profit" value={`$${data.today.profit.toFixed(2)}`} sub={`${data.today.profit_margin.toFixed(1)}% margin`} color="blue" />
          <StatCard icon={ShoppingBag} label="Orders" value={`${data.today.orders}`} color="purple" />
          <StatCard icon={Package} label="Active Products" value={`${data.all_time.active_products}`} color="orange" />
        </div>
      </div>

      {/* All-time */}
      <div className="mt-6 mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">All Time</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatCard icon={DollarSign} label="Total Revenue" value={`$${data.all_time.revenue.toFixed(2)}`} color="green" />
          <StatCard icon={TrendingUp} label="Total Profit" value={`$${data.all_time.profit.toFixed(2)}`} color="blue" />
          <StatCard icon={ShoppingBag} label="Total Orders" value={`${data.all_time.orders}`} color="purple" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Orders */}
        <div className="lg:col-span-2 card p-6">
          <h2 className="font-bold text-white mb-4 flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-brand-400" />
            Recent Orders
          </h2>
          {data.recent_orders.length === 0 ? (
            <p className="text-gray-600 text-sm">No orders yet. Share your store!</p>
          ) : (
            <div className="space-y-3">
              {data.recent_orders.map((order) => (
                <div key={order.order_number} className="flex items-center justify-between py-2 border-b border-dark-700 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-white">#{order.order_number}</p>
                    <p className="text-xs text-gray-500">{order.customer}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-white">${order.total.toFixed(2)}</p>
                    <p className={`text-xs capitalize ${STATUS_COLORS[order.status] || "text-gray-400"}`}>
                      {order.status.replace(/_/g, " ")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-6">
          {/* Security status */}
          <div className="card p-6">
            <h2 className="font-bold text-white mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-brand-400" />
              Security Status
            </h2>
            {data.security_status ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  {data.security_status.risk_level === "low" ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-orange-400" />
                  )}
                  <span className={`font-semibold capitalize ${RISK_COLORS[data.security_status.risk_level]}`}>
                    {data.security_status.risk_level} Risk
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  {data.security_status.findings_count} findings
                </p>
                <p className="text-xs text-gray-600">
                  Last scan: {new Date(data.security_status.last_scan).toLocaleString()}
                </p>
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No scan run yet</p>
            )}
          </div>

          {/* AI Report */}
          <div className="card p-6">
            <h2 className="font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-brand-400" />
              AI Daily Report
            </h2>
            {data.latest_ai_report ? (
              <div className="space-y-3">
                <p className="text-xs text-gray-600 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {data.latest_ai_report.date}
                </p>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {data.latest_ai_report.executive_summary}
                </p>
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No report yet — runs at 6am UTC daily</p>
            )}
          </div>
        </div>
      </div>

      {/* Automation Controls */}
      <div className="mt-8 card p-6">
        <h2 className="font-bold text-white mb-2 flex items-center gap-2">
          <Zap className="w-5 h-5 text-brand-400" />
          Manual Automation Triggers
        </h2>
        <p className="text-gray-600 text-sm mb-5">
          All tasks run automatically on schedule. Use these buttons to trigger them immediately.
        </p>
        <div className="flex flex-wrap gap-3">
          {automationTasks.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => triggerTask(id)}
              disabled={triggering !== null}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all ${
                triggering === id
                  ? "border-brand-500 bg-brand-900/40 text-brand-300"
                  : "border-dark-600 hover:border-brand-700 text-gray-300 hover:text-white hover:bg-dark-700"
              }`}
            >
              {triggering === id ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {triggering === id ? "Running..." : label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
