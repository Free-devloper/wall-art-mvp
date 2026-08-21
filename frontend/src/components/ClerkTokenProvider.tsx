import { useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { setClerkTokenGetter } from '../lib/api';

export default function ClerkTokenProvider({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();
  
  useEffect(() => {
    setClerkTokenGetter(getToken);
    return () => setClerkTokenGetter(() => Promise.resolve(null));
  }, [getToken]);
  
  return <>{children}</>;
}
