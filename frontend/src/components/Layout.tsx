import { Outlet, Link } from 'react-router-dom';
import { Camera } from 'lucide-react';
import { SignedIn, SignedOut, UserButton, SignInButton, SignUpButton } from '@clerk/clerk-react';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 bg-brand-navy text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <Camera className="w-8 h-8 text-brand-gold" />
            <span className="font-bold text-xl tracking-tight">Wall Art</span>
          </Link>
          <nav className="flex items-center space-x-6">
            <Link to="/themes" className="hover:text-brand-gold transition-colors text-sm font-medium">Themes</Link>
            
            <SignedIn>
              <UserButton
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: 'w-8 h-8 ring-2 ring-brand-gold/50',
                  }
                }}
              />
            </SignedIn>
            
            <SignedOut>
              <SignInButton mode="modal">
                <button className="text-sm font-medium hover:text-brand-gold transition-colors">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-brand-gold text-gray-900 px-4 py-2 rounded-lg text-sm font-bold hover:bg-yellow-500 transition-colors">
                  Get Started
                </button>
              </SignUpButton>
            </SignedOut>
          </nav>
        </div>
      </header>
      
      <main className="flex-grow flex flex-col">
        <Outlet />
      </main>

      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2 text-white mb-4">
              <Camera className="w-6 h-6 text-brand-gold" />
              <span className="font-bold text-lg">Wall Art</span>
            </div>
            <p className="text-sm">Turn your photo into stunning AI-powered wall art.</p>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Contact</h3>
            <p className="text-sm">support@wallart.example.com</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
