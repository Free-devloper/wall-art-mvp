import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { adminGetOrder, adminUpdateOrderStatus, adminDeletePhotos, adminGetProductionFile } from '../../lib/api';
import type { AdminOrder } from '../../types';
import OrderStatusBadge from '../../components/OrderStatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import { formatPrice } from '../../lib/utils';

export default function AdminOrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<AdminOrder | null>(null);

  const fetchOrder = () => {
    adminGetOrder(id!).then(res => setOrder(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const handleStatusChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    try {
      await adminUpdateOrderStatus(id!, e.target.value);
      fetchOrder();
    } catch (err) {
      console.error(err);
      alert('Error updating status');
    }
  };

  const handleDeletePhotos = async () => {
    if (window.confirm('Are you sure? This cannot be undone.')) {
      try {
        await adminDeletePhotos(id!);
        alert('Photos deleted successfully');
        fetchOrder();
      } catch (err) {
        console.error(err);
        alert('Error deleting photos');
      }
    }
  };

  const handleDownloadProductionFile = async () => {
    try {
      const res = await adminGetProductionFile(id!);
      const url = res.data?.production_url;
      if (url) {
        // Rewrite backend URL to go through Vite proxy
        const proxyUrl = url.replace('http://localhost:8000', '');
        window.open(proxyUrl, '_blank');
      } else {
        alert('No production file available');
      }
    } catch (err) {
      console.error(err);
      alert('No production file available for this order');
    }
  };

  if (!order) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" message="Loading order..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-4">
            Order #{order.id.slice(0, 8)}
            <OrderStatusBadge status={order.status} />
          </h1>
          <p className="text-gray-400 mt-1">{order.customer_name} ({order.customer_email})</p>
        </div>
        
        <div>
          <select 
            value={order.status} 
            onChange={handleStatusChange}
            className="bg-gray-800 border border-gray-700 text-white text-sm rounded-lg block p-2"
          >
            <option value="new">New</option>
            <option value="paid">Paid</option>
            <option value="in_production">In Production</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-gray-800 rounded-lg p-6 shadow">
            <h2 className="text-lg font-bold text-white mb-4">Generations</h2>
            <div className="grid grid-cols-2 gap-4">
              {order.generations?.map((gen, idx) => (
                <div key={gen.id} className="border border-gray-700 rounded p-2">
                  <span className="text-xs text-gray-400 block mb-2">Attempt {idx + 1} - {gen.status}</span>
                  {gen.preview_url && <img src={gen.preview_url} alt="preview" className="w-full h-auto rounded" />}
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6 shadow">
            <h2 className="text-lg font-bold text-white mb-4">Order Details</h2>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-gray-700 pb-2">
                <dt className="text-gray-400">Total</dt>
                <dd className="text-white font-medium">{order.price_cents ? formatPrice(order.price_cents) : '-'}</dd>
              </div>
              <div className="flex justify-between border-b border-gray-700 pb-2">
                <dt className="text-gray-400">Payment Status</dt>
                <dd className="text-white font-medium">{order.payment_status}</dd>
              </div>
              <div className="flex justify-between border-b border-gray-700 pb-2">
                <dt className="text-gray-400">Theme ID</dt>
                <dd className="text-white font-medium">{order.theme_id}</dd>
              </div>
              
              {(order.shipping_address_line1 || order.shipping_city) && (
                <div className="pt-2">
                  <dt className="text-gray-400 mb-1">Shipping Address</dt>
                  <dd className="text-white">
                    {order.customer_name}<br/>
                    {order.shipping_address_line1}<br/>
                    {order.shipping_address_line2 && <>{order.shipping_address_line2}<br/></>}
                    {order.shipping_city}, {order.shipping_postcode}<br/>
                    {order.shipping_country}
                  </dd>
                </div>
              )}
            </dl>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 shadow">
            <h2 className="text-lg font-bold text-white mb-4">Actions</h2>
            <button onClick={handleDownloadProductionFile} className="w-full bg-brand-gold text-gray-900 py-2 rounded font-medium mb-3 hover:bg-brand-amber">Download Production File</button>
            <button onClick={handleDeletePhotos} className="w-full border border-red-500 text-red-500 py-2 rounded font-medium hover:bg-red-500/10">Delete Photos</button>
          </div>
        </div>
      </div>
    </div>
  );
}
