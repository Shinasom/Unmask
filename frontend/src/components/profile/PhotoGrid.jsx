// frontend/src/components/profile/PhotoGrid.jsx
"use client";

import { useState } from "react";
import { ImageIcon, Heart, MessageCircle, Lock } from "lucide-react";
import PhotoModal from "./PhotoModal";

export default function PhotoGrid({ photos, isOwnProfile, onPhotoDelete }) {
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [hoveredPhoto, setHoveredPhoto] = useState(null);

  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith("http")) return path;
    return `http://127.0.0.1:8000${path}`;
  };

  if (!photos || photos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="w-16 h-16 rounded-full border-2 border-gray-900 flex items-center justify-center mb-4">
          <ImageIcon className="w-8 h-8 text-gray-900" />
        </div>
        <h3 className="text-2xl font-light text-gray-900 mb-2">
          No Posts Yet
        </h3>
        <p className="text-gray-500 text-sm">
          {isOwnProfile ? "Share your first photo" : "No photos to show"}
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-3 gap-1 md:gap-7">
        {photos.map((photo) => {
          const imageUrl = getImageUrl(photo.public_image || photo.original_image);
          const requiresConsent = photo.requires_consent;

          return (
            <div
              key={photo.id}
              className="relative aspect-square cursor-pointer group"
              onClick={() => setSelectedPhoto(photo)}
              onMouseEnter={() => setHoveredPhoto(photo.id)}
              onMouseLeave={() => setHoveredPhoto(null)}
            >
              {/* Image */}
              <img
                src={imageUrl}
                alt={photo.caption || "Photo"}
                className="w-full h-full object-cover transition-opacity group-hover:opacity-90"
                onError={(e) => {
                  e.target.src =
                    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Crect width='400' height='400' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='24' fill='%239ca3af'%3EImage%3C/text%3E%3C/svg%3E";
                }}
              />

              {/* Hover Overlay with Stats */}
              {hoveredPhoto === photo.id && (
                <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center gap-6 transition-opacity">
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <Heart className="w-5 h-5 fill-white" />
                    <span>{photo.likes_count || 0}</span>
                  </div>
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <MessageCircle className="w-5 h-5 fill-white" />
                    <span>{photo.comments_count || 0}</span>
                  </div>
                </div>
              )}

              {/* Privacy indicator */}
              {requiresConsent && (
                <div className="absolute top-2 right-2 bg-black bg-opacity-60 backdrop-blur-sm rounded-full p-1.5">
                  <Lock className="w-3 h-3 text-white" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Photo Modal */}
      {selectedPhoto && (
        <PhotoModal
          photo={selectedPhoto}
          isOwnProfile={isOwnProfile}
          onClose={() => setSelectedPhoto(null)}
          onDelete={onPhotoDelete}
        />
      )}
    </>
  );
}