import React from 'react';

export interface AddressData {
  name: string;
  line1: string;
  line2: string;
  city: string;
  postcode: string;
  country: string;
}

interface AddressFormProps {
  value: AddressData;
  onChange: (data: AddressData) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
}

export default function AddressForm({ value, onChange, onSubmit, loading }: AddressFormProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...value, [e.target.name]: e.target.value });
  };

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
        <input required name="name" value={value.name} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
        <input required name="line1" value={value.line1} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2 (Optional)</label>
        <input name="line2" value={value.line2} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Town / City</label>
          <input required name="city" value={value.city} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Postcode</label>
          <input required name="postcode" value={value.postcode} onChange={handleChange} pattern="^([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}|GIR ?0A{2})$" title="Please enter a valid UK postcode" className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-gold uppercase focus:border-transparent outline-none" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
        <input required name="country" value={value.country} disabled className="w-full p-3 border border-gray-200 bg-gray-50 rounded-lg text-gray-500 cursor-not-allowed" />
      </div>
      <button type="submit" disabled={loading} className="w-full mt-6 bg-brand-navy hover:bg-brand-navy/90 text-white py-4 rounded-xl font-semibold transition-colors disabled:opacity-50">
        {loading ? 'Processing...' : 'Pay with Stripe'}
      </button>
    </form>
  );
}
