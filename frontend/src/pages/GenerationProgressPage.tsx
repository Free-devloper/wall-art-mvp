import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import GenerationProgress from '../components/GenerationProgress';
import { getGenerationStatus } from '../lib/api';

export default function GenerationProgressPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState('queued');
  const [error, setError] = useState(false);

  useEffect(() => {
    // Poll immediately, then every 3 seconds
    const poll = async () => {
      try {
        const { data } = await getGenerationStatus(id!);
        setStatus(data.status);
        if (data.status === 'completed') {
          clearInterval(interval);
          setTimeout(() => navigate(`/order/${id}/preview`), 1000);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setError(true);
        }
      } catch (err) {
        console.error(err);
      }
    };

    poll(); // immediate first check
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [id, navigate]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] p-4 text-center">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Generation Failed</h2>
        <p className="text-gray-600 mb-6">We encountered an error generating your artwork. Please contact support.</p>
        <button onClick={() => window.location.reload()} className="bg-brand-navy text-white px-6 py-2 rounded-lg">Retry</button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-20 px-4 bg-gray-50">
      <h1 className="text-3xl font-bold text-brand-navy mb-12 text-center">Creating Your Masterpiece</h1>
      <GenerationProgress status={status} />
    </div>
  );
}
