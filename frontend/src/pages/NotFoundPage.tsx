import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-6xl font-black text-brand-navy mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">Oops! The page you're looking for doesn't exist.</p>
      <Link to="/" className="bg-brand-navy text-white px-8 py-3 rounded-full font-medium hover:bg-brand-navy/90 transition-colors">
        Go Back Home
      </Link>
    </div>
  );
}
