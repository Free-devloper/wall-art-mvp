import { useState } from 'react';
import { ZoomIn } from 'lucide-react';

export default function ImagePreview({ src }: { src: string }) {
  const [zoomed, setZoomed] = useState(false);

  return (
    <div className="relative group overflow-hidden rounded-xl bg-gray-100">
      <img 
        src={src} 
        alt="Artwork Preview" 
        className={`w-full h-auto transition-transform duration-300 cursor-pointer ${
          zoomed ? 'scale-150' : 'scale-100'
        }`}
        onClick={() => setZoomed(!zoomed)}
      />
      <div className="absolute top-4 left-4 bg-black/70 text-white text-xs font-bold px-3 py-1 rounded backdrop-blur-sm tracking-widest">
        PREVIEW
      </div>
      <button 
        className="absolute bottom-4 right-4 bg-white/90 p-2 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => setZoomed(!zoomed)}
      >
        <ZoomIn className="w-5 h-5 text-gray-700" />
      </button>
    </div>
  );
}
