import { Camera } from 'lucide-react';
import { cn } from '../lib/utils';

interface LoadingSpinnerProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export default function LoadingSpinner({ className, size = 'md', message }: LoadingSpinnerProps) {
  const sizeConfig = {
    sm: { icon: 'w-5 h-5', text: 'text-xs', ring: 'w-8 h-8', gap: 'gap-2' },
    md: { icon: 'w-8 h-8', text: 'text-sm', ring: 'w-14 h-14', gap: 'gap-3' },
    lg: { icon: 'w-12 h-12', text: 'text-base', ring: 'w-20 h-20', gap: 'gap-4' },
  };

  const cfg = sizeConfig[size];

  return (
    <div className={cn("flex flex-col justify-center items-center", cfg.gap, className)}>
      {/* Animated logo ring */}
      <div className="relative">
        {/* Spinning ring */}
        <div className={cn(
          "rounded-full border-2 border-gray-200 border-t-brand-gold animate-spin",
          cfg.ring
        )} />
        {/* Static camera icon in center */}
        <div className="absolute inset-0 flex items-center justify-center">
          <Camera className={cn("text-brand-gold animate-pulse", cfg.icon)} />
        </div>
      </div>
      
      {/* Optional loading message */}
      {message && (
        <p className={cn("text-gray-500 font-medium animate-pulse", cfg.text)}>
          {message}
        </p>
      )}
    </div>
  );
}
