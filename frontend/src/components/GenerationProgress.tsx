import { Camera, CheckCircle2 } from 'lucide-react';

interface GenerationProgressProps {
  status: string;
}

export default function GenerationProgress({ status }: GenerationProgressProps) {
  // Backend statuses (lowercase): queued, processing, completed, failed
  const stages = [
    { id: 'queued', label: 'Preparing order' },
    { id: 'processing', label: 'Generating artwork' },
    { id: 'completed', label: 'Completed' },
  ];

  const currentIndex = Math.max(0, stages.findIndex(s => s.id === status));

  return (
    <div className="w-full max-w-md mx-auto space-y-8 p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
      {/* Animated logo */}
      <div className="flex justify-center mb-4">
        {status === 'completed' ? (
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-green-50 flex items-center justify-center">
              <CheckCircle2 className="w-12 h-12 text-green-500" />
            </div>
          </div>
        ) : (
          <div className="relative">
            {/* Spinning ring */}
            <div className="w-20 h-20 rounded-full border-[3px] border-gray-200 border-t-brand-gold animate-spin" />
            {/* Camera icon in center */}
            <div className="absolute inset-0 flex items-center justify-center">
              <Camera className="w-10 h-10 text-brand-gold animate-pulse" />
            </div>
          </div>
        )}
      </div>

      {/* Stage indicators */}
      <div className="space-y-4 relative">
        {stages.map((stage, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div key={stage.id} className="flex items-center gap-4">
              <div className="relative flex-shrink-0">
                <div className={`w-4 h-4 rounded-full transition-all duration-500 ${
                  isCompleted ? 'bg-green-500 scale-100' : isCurrent ? 'bg-brand-gold scale-110' : 'bg-gray-200 scale-100'
                }`} />
                {isCurrent && (
                  <div className="absolute inset-0 w-4 h-4 rounded-full bg-brand-gold animate-ping opacity-30" />
                )}
              </div>
              <span className={`text-sm font-medium transition-colors duration-300 ${
                isCompleted ? 'text-gray-400 line-through' : isCurrent ? 'text-brand-navy font-semibold' : 'text-gray-300'
              }`}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
