import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getThemes } from '../lib/api';
import type { Theme } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import { Palette } from 'lucide-react';

function formatPrice(cents: number): string {
  return `£${(cents / 100).toFixed(2)}`;
}

export default function ThemeGalleryPage() {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getThemes()
      .then(res => {
        setThemes(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-24"><LoadingSpinner size="lg" /></div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-extrabold text-brand-navy tracking-tight mb-4">Choose Your Theme</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Select a style for your artwork. Our AI will seamlessly blend your photo into the theme you choose.
        </p>
      </div>

      {themes.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <Palette className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No themes available yet. Check back soon!</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {themes.map(theme => (
            <div key={theme.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-md transition-shadow">
              <div className="aspect-[4/3] bg-gradient-to-br from-brand-navy/10 to-brand-gold/10 relative overflow-hidden flex items-center justify-center">
                {theme.example_image_url ? (
                  <img src={theme.example_image_url} alt={theme.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                ) : (
                  <div className="text-center p-6">
                    <Palette className="w-16 h-16 mx-auto mb-3 text-brand-navy/30" />
                    <p className="text-brand-navy/50 font-medium">{theme.name}</p>
                  </div>
                )}
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold text-brand-navy mb-2">{theme.name}</h3>
                <p className="text-gray-600 mb-6 text-sm line-clamp-2">{theme.description}</p>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-lg text-brand-navy">
                    From {formatPrice(theme.price_cents)}
                  </span>
                  <Link
                    to={`/upload?theme=${theme.id}`}
                    className="bg-brand-navy text-white px-5 py-2.5 rounded-lg font-medium hover:bg-brand-navy/90 transition-colors"
                  >
                    Select
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
