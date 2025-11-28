// frontend/src/components/profile/PhotoModal.jsx
"use client";

import { useState, useEffect } from "react";
import { X, MoreVertical, Heart, MessageCircle, Send, Bookmark, Smile } from "lucide-react";
import { useRouter } from "next/navigation";
import DeleteModal from "./DeleteModal";

export default function PhotoModal({ photo, isOwnProfile, onClose, onDelete }) {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showOptionsMenu, setShowOptionsMenu] = useState(false);
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const router = useRouter();

  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith("http")) return path;
    return `http://127.0.0.1:8000${path}`;
  };

  const getAvatarUrl = () => {
    const profilePicUrl = getImageUrl(photo.uploader?.profile_pic);
    if (profilePicUrl) return profilePicUrl;
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(
      photo.uploader?.username || "User"
    )}&size=48&background=556B2F&color=fff&bold=true`;
  };

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const handleCopyLink = () => {
    const url = `${window.location.origin}/photo/${photo.id}`;
    navigator.clipboard.writeText(url);
    alert("Link copied to clipboard!");
    setShowOptionsMenu(false);
  };

  const handleDelete = () => {
    setShowOptionsMenu(false);
    setShowDeleteModal(true);
  };

  const handleDeleteSuccess = (photoId) => {
    onDelete(photoId);
    onClose();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return "just now";
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg overflow-hidden max-w-6xl w-full max-h-[90vh] flex flex-col md:flex-row"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image Section */}
        <div className="flex-shrink-0 bg-black flex items-center justify-center md:w-[60%]">
          <img
            src={getImageUrl(photo.public_image || photo.original_image)}
            alt={photo.caption || "Photo"}
            className="max-w-full max-h-[90vh] object-contain"
          />
        </div>

        {/* Info Section */}
        <div className="flex flex-col md:w-[40%] max-h-[90vh]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <img
                src={getAvatarUrl()}
                alt={photo.uploader?.username}
                className="w-10 h-10 rounded-full object-cover cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => router.push(`/profile/${photo.uploader?.username}`)}
              />
              <button
                onClick={() => router.push(`/profile/${photo.uploader?.username}`)}
                className="font-semibold text-sm text-gray-900 hover:text-gray-600 truncate"
              >
                {photo.uploader?.username}
              </button>
            </div>

            {isOwnProfile && (
              <div className="relative">
                <button
                  onClick={() => setShowOptionsMenu(!showOptionsMenu)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  aria-label="More options"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>

                {showOptionsMenu && (
                  <div className="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-2 w-48 z-10">
                    <button
                      onClick={handleCopyLink}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 transition-colors"
                    >
                      Copy link
                    </button>
                    <button
                      onClick={handleDelete}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-50 transition-colors"
                    >
                      Delete photo
                    </button>
                  </div>
                )}
              </div>
            )}

            <button
              onClick={onClose}
              className="md:hidden p-2 hover:bg-gray-100 rounded-full transition-colors ml-2"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Caption and Comments */}
          <div className="flex-1 overflow-y-auto p-4">
            {/* Original Caption */}
            {photo.caption && (
              <div className="flex gap-3 mb-4">
                <img
                  src={getAvatarUrl()}
                  alt={photo.uploader?.username}
                  className="w-10 h-10 rounded-full object-cover flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2 mb-1">
                    <button
                      onClick={() => router.push(`/profile/${photo.uploader?.username}`)}
                      className="font-semibold text-sm hover:text-gray-600"
                    >
                      {photo.uploader?.username}
                    </button>
                    <span className="text-sm text-gray-500 flex-shrink-0">
                      {formatDate(photo.uploaded_at)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-900 break-words">
                    {photo.caption}
                  </p>
                </div>
              </div>
            )}

            {/* Comments would go here */}
            <div className="text-sm text-gray-500 text-center py-8">
              No comments yet
            </div>
          </div>

          {/* Actions */}
          <div className="border-t border-gray-200">
            {/* Action Buttons */}
            <div className="flex items-center justify-between p-3">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setLiked(!liked)}
                  className="hover:text-gray-500 transition-colors"
                  aria-label="Like"
                >
                  <Heart
                    className={`w-6 h-6 ${liked ? "fill-red-500 text-red-500" : ""}`}
                  />
                </button>
                <button
                  className="hover:text-gray-500 transition-colors"
                  aria-label="Comment"
                >
                  <MessageCircle className="w-6 h-6" />
                </button>
                <button
                  className="hover:text-gray-500 transition-colors"
                  aria-label="Share"
                >
                  <Send className="w-6 h-6" />
                </button>
              </div>
              <button
                onClick={() => setSaved(!saved)}
                className="hover:text-gray-500 transition-colors"
                aria-label="Save"
              >
                <Bookmark
                  className={`w-6 h-6 ${saved ? "fill-gray-900" : ""}`}
                />
              </button>
            </div>

            {/* Like Count */}
            <div className="px-4 pb-2">
              <button className="font-semibold text-sm hover:text-gray-600">
                {photo.likes_count || 0} likes
              </button>
            </div>

            {/* Timestamp */}
            <div className="px-4 pb-3">
              <time className="text-xs text-gray-500 uppercase">
                {formatDate(photo.uploaded_at)}
              </time>
            </div>

            {/* Comment Input */}
            <div className="flex items-center gap-3 p-3 border-t border-gray-200">
              <button className="hover:text-gray-500">
                <Smile className="w-6 h-6" />
              </button>
              <input
                type="text"
                placeholder="Add a comment..."
                className="flex-1 text-sm outline-none"
              />
              <button className="text-[#0095F6] font-semibold text-sm hover:text-[#0082D9] disabled:opacity-40">
                Post
              </button>
            </div>
          </div>
        </div>

        {/* Close button for desktop */}
        <button
          onClick={onClose}
          className="hidden md:block absolute top-4 right-4 text-white hover:text-gray-300 transition-colors"
          aria-label="Close"
        >
          <X className="w-8 h-8" />
        </button>
      </div>

      {/* Delete Modal */}
      {showDeleteModal && (
        <DeleteModal
          photoId={photo.id}
          onClose={() => setShowDeleteModal(false)}
          onDeleteSuccess={handleDeleteSuccess}
        />
      )}
    </div>
  );
}