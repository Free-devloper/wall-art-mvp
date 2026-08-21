import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import ConsentCheckbox from '../components/ConsentCheckbox';
import { requestUploadUrl, createOrder, requestGeneration } from '../lib/api';
import axios from 'axios';

export default function UploadPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const themeId = searchParams.get('theme') || '';
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [instructions, setInstructions] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !consent || !email || !name || !themeId) return;

    setLoading(true);
    setError('');
    try {
      // Step 1: Get upload URL from backend
      const { data: uploadData } = await requestUploadUrl(email, consent);

      // Step 2: Upload file to the returned URL
      // For local storage mode: POST as multipart form data
      // For S3 mode: PUT/POST to presigned URL
      const uploadUrl = uploadData.upload_url;
      if (uploadUrl.includes('/api/local-storage/upload')) {
        // Local storage mode — send as FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('key', uploadData.fields.key);
        await axios.post(uploadUrl, formData);
      } else {
        // S3 presigned POST
        const formData = new FormData();
        Object.entries(uploadData.fields).forEach(([k, v]) => formData.append(k, v));
        formData.append('file', file);
        await axios.post(uploadUrl, formData);
      }

      // Step 3: Create order
      const { data: order } = await createOrder({
        theme_id: themeId,
        upload_id: uploadData.upload_id,
        instructions: instructions || undefined,
        product_size: 'A2',  // default — user picks exact size later
        customer_email: email,
        customer_name: name,
      });

      // Step 4: Trigger generation
      await requestGeneration(order.id, instructions || undefined);

      // Step 5: Navigate to progress page
      navigate(`/order/${order.id}/progress`);
    } catch (err: unknown) {
      console.error(err);
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Upload failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-brand-navy mb-8">Upload Your Photo</h1>

      {!themeId && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <p className="text-amber-800 text-sm">
            Please <a href="/themes" className="underline font-medium">select a theme</a> first.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        <FileUploader onFileSelect={setFile} />
        <ConsentCheckbox checked={consent} onChange={setConsent} />
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-700">Your Name *</label>
          <input
            type="text"
            required
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-gold"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-700">Email Address *</label>
          <input
            type="email"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-gold"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-700">
            Optional Instructions
            <span className="text-gray-400 font-normal ml-2">({instructions.length}/500)</span>
          </label>
          <textarea
            rows={3}
            maxLength={500}
            value={instructions}
            onChange={e => setInstructions(e.target.value)}
            placeholder="Describe any special requests. Note: we cannot include copyrighted characters, logos, or branded content."
            className="w-full p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-gold"
          />
        </div>
        <button
          type="submit"
          disabled={!file || !consent || !email || !name || !themeId || loading}
          className="w-full bg-brand-navy text-white py-4 rounded-xl font-bold disabled:opacity-50 hover:bg-brand-navy/90 transition-colors"
        >
          {loading ? 'Processing...' : 'Generate My Artwork'}
        </button>
      </form>
    </div>
  );
}
