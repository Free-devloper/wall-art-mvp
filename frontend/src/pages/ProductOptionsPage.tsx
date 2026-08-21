import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import SizeSelector from '../components/SizeSelector';
import { formatPrice } from '../lib/utils';
import { PRODUCT_SIZES } from '../types';

export default function ProductOptionsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedSize, setSelectedSize] = useState('');

  const sizes = PRODUCT_SIZES;

  const selectedSizeData = sizes.find(s => s.id === selectedSize);

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-brand-navy mb-8">Choose Your Size</h1>
      
      <div className="grid md:grid-cols-2 gap-12">
        <div>
          <div className="bg-gray-200 aspect-[3/4] rounded-xl flex items-center justify-center">
            {/* Small preview placeholder */}
            <span className="text-gray-400">Artwork Preview</span>
          </div>
        </div>
        
        <div className="space-y-8">
          <div>
            <h3 className="text-xl font-semibold mb-4">Select Size</h3>
            <SizeSelector sizes={sizes} selectedId={selectedSize} onSelect={setSelectedSize} />
          </div>
          
          <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
            <div className="flex justify-between items-center mb-6">
              <span className="text-lg font-medium">Total</span>
              <span className="text-2xl font-bold text-brand-navy">
                {selectedSizeData ? formatPrice(selectedSizeData.price_cents) : '---'}
              </span>
            </div>
            
            <button 
              disabled={!selectedSize}
              onClick={() => navigate(`/order/${id}/checkout?size=${selectedSize}`)}
              className="w-full bg-brand-gold hover:bg-brand-amber text-brand-navy py-4 rounded-xl font-bold text-lg transition-colors disabled:opacity-50"
            >
              Continue to Checkout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
