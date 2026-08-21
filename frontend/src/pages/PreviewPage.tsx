import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ImagePreview from '../components/ImagePreview';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import { getGenerationStatus, requestRegeneration, approvePreview } from '../lib/api';

export default function PreviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [regenLoading, setRegenLoading] = useState(false);
  const [regenerationsLeft, setRegenerationsLeft] = useState(2);

  useEffect(() => {
    getGenerationStatus(id!).then(res => {
      setUrl(res.data.preview_url || '');
      setRegenerationsLeft(res.data.remaining_regenerations);
    }).catch(console.error);
  }, [id]);

  const handleApprove = async () => {
    await approvePreview(id!);
    navigate(`/order/${id}/options`);
  };

  const handleRegenerate = async () => {
    setRegenLoading(true);
    try {
      await requestRegeneration(id!, reason);
      setIsModalOpen(false);
      navigate(`/order/${id}/progress`);
    } catch (err) {
      console.error(err);
    } finally {
      setRegenLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-brand-navy mb-2">Review Your Artwork</h1>
        <p className="text-gray-600">This is a preview of your artwork. The final print will be high-resolution without watermark.</p>
      </div>
      
      {url ? <ImagePreview src={url} /> : (
        <div className="flex justify-center items-center aspect-[4/3] rounded-xl mb-8 bg-gray-50">
          <LoadingSpinner size="lg" message="Loading preview..." />
        </div>
      )}
      
      <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          onClick={handleApprove}
          className="bg-brand-navy text-white px-8 py-4 rounded-xl font-bold hover:bg-brand-navy/90 transition-colors"
        >
          I Love It! Continue
        </button>
        <button 
          onClick={() => setIsModalOpen(true)}
          disabled={regenerationsLeft <= 0}
          className="bg-gray-100 text-gray-700 px-8 py-4 rounded-xl font-bold hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          Regenerate ({regenerationsLeft} remaining)
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Request Regeneration">
        <div className="space-y-4">
          <p className="text-gray-600">Tell us what you'd like us to change or improve (optional):</p>
          <textarea 
            rows={4} 
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-gold"
          ></textarea>
          <button 
            onClick={handleRegenerate} 
            disabled={regenLoading}
            className="w-full bg-brand-navy text-white py-3 rounded-lg font-bold"
          >
            {regenLoading ? 'Requesting...' : 'Regenerate Artwork'}
          </button>
        </div>
      </Modal>
    </div>
  );
}
