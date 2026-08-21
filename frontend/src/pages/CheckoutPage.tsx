import { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import AddressForm, { AddressData } from '../components/AddressForm';
import { createCheckoutSession } from '../lib/api';

export default function CheckoutPage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const sizeId = searchParams.get('size') || 'm';
  
  const [address, setAddress] = useState<AddressData>({
    name: '', line1: '', line2: '', city: '', postcode: '', country: 'United Kingdom'
  });
  const [loading, setLoading] = useState(false);

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await createCheckoutSession(id!);
      window.location.href = data.checkout_url; // Redirect to Stripe
    } catch (err) {
      console.error(err);
      alert('Checkout failed.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-brand-navy mb-8">Checkout</h1>
      <div className="grid md:grid-cols-2 gap-12">
        <div className="order-2 md:order-1">
          <h2 className="text-xl font-bold mb-6">Delivery Details</h2>
          <AddressForm value={address} onChange={setAddress} onSubmit={handleCheckout} loading={loading} />
        </div>
        <div className="order-1 md:order-2">
          <div className="bg-gray-50 p-8 rounded-2xl border border-gray-100 sticky top-24">
            <h2 className="text-xl font-bold mb-6">Order Summary</h2>
            <div className="flex gap-4 mb-6 pb-6 border-b border-gray-200">
              <div className="w-24 h-24 bg-gray-200 rounded-lg flex-shrink-0"></div>
              <div>
                <h3 className="font-semibold text-lg">Custom Wall Art</h3>
                <p className="text-gray-600">Size: {sizeId.toUpperCase()}</p>
              </div>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">£49.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className="font-medium">Free</span>
              </div>
              <div className="flex justify-between text-lg font-bold pt-3 border-t border-gray-200 mt-3">
                <span>Total</span>
                <span>£49.00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
