import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import { getOrderConfirmation } from '../lib/api';

interface ConfirmationResponse {
  order_id: string;
  status: string;
  customer_email: string;
  total_cents: number;
}

export default function ConfirmationPage() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<ConfirmationResponse | null>(null);

  useEffect(() => {
    getOrderConfirmation(id!).then(res => setOrder(res.data)).catch(console.error);
  }, [id]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-20 text-center">
      <CheckCircle2 className="w-24 h-24 text-green-500 mx-auto mb-6" />
      <h1 className="text-4xl font-bold text-brand-navy mb-4">Thank you for your order!</h1>
      <p className="text-lg text-gray-600 mb-8">
        You will receive a confirmation email at <span className="font-semibold">{order?.customer_email || 'your email'}</span>.
      </p>
      
      <div className="bg-gray-50 p-8 rounded-2xl border border-gray-100 mb-8 max-w-lg mx-auto text-left">
        <h2 className="font-bold text-lg mb-4">What happens next?</h2>
        <ul className="space-y-4 text-gray-700">
          <li className="flex gap-3">
            <span className="font-bold text-brand-gold">1.</span>
            <span>Your artwork is now being prepared for production.</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-brand-gold">2.</span>
            <span>We print it on premium vinyl using our high-end printers.</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-brand-gold">3.</span>
            <span>It will be carefully packaged and shipped to your address within 3-5 business days.</span>
          </li>
        </ul>
      </div>

      <Link to="/" className="text-brand-navy font-semibold hover:underline">Return to Home</Link>
    </div>
  );
}
