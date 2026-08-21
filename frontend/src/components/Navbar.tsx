import { SignedIn, SignedOut, UserButton } from '@clerk/clerk-react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="bg-brand-navy border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-white">Wall<span className="text-brand-gold">Art</span></span>
          </Link>
          
          <div className="flex items-center gap-6">
            <Link to="/themes" className="text-gray-300 hover:text-white text-sm font-medium">Themes</Link>
            
            <SignedIn>
              <Link to="/my-orders" className="text-gray-300 hover:text-white text-sm font-medium">My Orders</Link>
              <UserButton 
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: 'w-8 h-8',
                  }
                }}
              />
            </SignedIn>
            
            <SignedOut>
              <Link to="/sign-in" className="text-gray-300 hover:text-white text-sm font-medium">Sign In</Link>
              <Link to="/sign-up" className="bg-brand-gold text-gray-900 px-4 py-2 rounded-lg text-sm font-bold hover:bg-yellow-500 transition-colors">Get Started</Link>
            </SignedOut>
          </div>
        </div>
      </div>
    </nav>
  );
}
