// frontend/src/components/profile/DeleteModal.jsx
'use client';

import { useState } from 'react';
import { Trash2, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function DeleteModal({ photoId, onClose, onConfirm }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    setIsDeleting(true);
    setError('');
    
    try {
      const response = await api.delete(`/api/photos/${photoId}/`);
      // DELETE returns 204 No Content on success
      onConfirm(photoId);
      onClose();
    } catch (err) {
      console.error('Delete error:', err);
      
      // 204 means success but no content - don't treat as error
      if (err.response?.status === 204) {
        onConfirm(photoId);
        onClose();
      } else {
        setError(err.response?.data?.error || 'Failed to delete. Please try again.');
        setIsDeleting(false);
      }
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl p-8 max-w-md w-full text-center"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Icon */}
        <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <Trash2 className="w-6 h-6 text-red-600" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Delete this photo?
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-6">
          This action cannot be undone. Your photo and all its data will be permanently deleted.
        </p>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3 justify-center">
          <button
            onClick={onClose}
            disabled={isDeleting}
            className="px-6 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-900 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isDeleting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}