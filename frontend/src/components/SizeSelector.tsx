import { formatPrice, cn } from '../lib/utils';
import type { ProductSize } from '../types';

interface SizeSelectorProps {
  sizes: ProductSize[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export default function SizeSelector({ sizes, selectedId, onSelect }: SizeSelectorProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {sizes.map((size) => (
        <button
          key={size.id}
          onClick={() => onSelect(size.id)}
          className={cn(
            "p-4 border-2 rounded-xl text-left transition-all",
            selectedId === size.id 
              ? "border-brand-gold bg-brand-gold/5" 
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          )}
        >
          <div className="flex justify-between items-center mb-1">
            <span className="font-semibold text-lg">{size.name}</span>
            <span className="font-bold text-brand-navy">{formatPrice(size.price_cents)}</span>
          </div>
          <div className="text-sm text-gray-500">{size.dimensions}</div>
        </button>
      ))}
    </div>
  );
}
