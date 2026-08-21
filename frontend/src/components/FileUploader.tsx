import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, X } from 'lucide-react';
import { cn } from '../lib/utils';

interface FileUploaderProps {
  onFileSelect: (file: File | null) => void;
  error?: string;
}

export default function FileUploader({ onFileSelect, error }: FileUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
    },
    maxSize: 20 * 1024 * 1024, // 20MB
    multiple: false,
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreview(null);
    onFileSelect(null);
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors flex flex-col items-center justify-center min-h-[250px]",
          isDragActive ? "border-brand-gold bg-brand-gold/5" : "border-gray-300 hover:border-gray-400 bg-white",
          isDragReject ? "border-red-500 bg-red-50" : "",
          error ? "border-red-500" : ""
        )}
      >
        <input {...getInputProps()} capture="environment" />
        
        {preview ? (
          <div className="relative w-full max-w-sm mx-auto">
            <img src={preview} alt="Preview" className="w-full h-auto rounded-lg shadow-sm" />
            <button
              onClick={removeFile}
              className="absolute -top-3 -right-3 bg-red-500 text-white rounded-full p-1 shadow-md hover:bg-red-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 text-gray-500">
            <UploadCloud className="w-12 h-12 text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700">Drag & drop your photo here</p>
              <p className="text-sm mt-1">or click to browse from your device</p>
            </div>
            <p className="text-xs text-gray-400 mt-4">Supports JPG, PNG, WEBP (Max 20MB)</p>
          </div>
        )}
      </div>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>
  );
}
