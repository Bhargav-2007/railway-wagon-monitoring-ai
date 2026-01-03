import React, { useCallback, useState } from 'react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isProcessing?: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onFileSelect, isProcessing }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  const borderClass = isDragging 
    ? 'border-purple-500 bg-purple-50' 
    : 'border-gray-300 hover:border-purple-400';
  
  const containerClass = `relative border-4 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer ${borderClass} ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`;

  return (
    <div
      className={containerClass}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        id="fileInput"
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        className="hidden"
        disabled={isProcessing}
      />
      
      <div className="space-y-4">
        <div className="text-6xl">📁</div>
        <div>
          <p className="text-xl font-semibold text-gray-700">
            {isProcessing ? 'Processing...' : 'Drop image here or click to browse'}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Supported: JPG, PNG (max 50MB)
          </p>
        </div>
      </div>

      {isProcessing && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600 font-medium">Analyzing image...</p>
          </div>
        </div>
      )}
    </div>
  );
};
