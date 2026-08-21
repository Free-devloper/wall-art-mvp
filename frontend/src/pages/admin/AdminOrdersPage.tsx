import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminGetOrders } from '../../lib/api';
import type { AdminOrder } from '../../types';
import OrderStatusBadge from '../../components/OrderStatusBadge';
import { formatDate, formatPrice } from '../../lib/utils';

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<AdminOrder[]>([]);
  const [status, setStatus] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [size, setSize] = useState<number>(10);
  
  const navigate = useNavigate();

  const fetchOrders = () => {
    adminGetOrders(page, status || undefined).then(res => {
      setOrders(res.data.items);
      setTotal(res.data.total);
      setSize(res.data.size);
      if (res.data.page) setPage(res.data.page);
    }).catch(console.error);
  };

  useEffect(() => {
    fetchOrders();
  }, [page, status]);

  const totalPages = Math.ceil(total / size) || 1;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Orders</h1>
        <div className="flex gap-4">
          <select 
            value={status} 
            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            className="bg-gray-800 border border-gray-700 text-white text-sm rounded-lg block p-2.5"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="paid">Paid</option>
            <option value="in_production">In Production</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>
      
      <div className="bg-gray-800 shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Order ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Customer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700 bg-gray-800">
            {orders.map((order) => (
              <tr key={order.id} onClick={() => navigate(`/admin/orders/${order.id}`)} className="hover:bg-gray-700 cursor-pointer transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">#{order.id.slice(0, 8)}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-white">{order.customer_name}</div>
                  <div className="text-sm text-gray-400">{order.customer_email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <OrderStatusBadge status={order.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{formatDate(order.created_at)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-medium">{order.price_cents ? formatPrice(order.price_cents) : '-'}</td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-400">No orders found.</td>
              </tr>
            )}
          </tbody>
        </table>
        
        {/* Pagination */}
        <div className="px-6 py-3 flex items-center justify-between border-t border-gray-700 bg-gray-900">
          <button 
            disabled={page <= 1} 
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 bg-gray-800 text-gray-300 rounded hover:bg-gray-700 disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-400">Page {page} of {totalPages}</span>
          <button 
            disabled={page >= totalPages} 
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 bg-gray-800 text-gray-300 rounded hover:bg-gray-700 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
