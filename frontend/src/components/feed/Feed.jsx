// =======================================================================
// /src/components/feed/Feed.jsx
// FIXED: More responsive with better spacing
// =======================================================================
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import Post from './Post';
import Moments from './Moments';
import { Loader2, ImageOff } from 'lucide-react';

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      if (!user) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const photosResponse = await api.get('/api/photos/');
        setPosts(photosResponse.data);  // No reverse needed - backend handles ordering
      } catch (error) {
        console.error("Failed to fetch feed data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="w-full flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Loading your feed...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4 md:space-y-6 pb-20 lg:pb-8">
      {/* Moments Section */}
      <Moments />

      {/* Posts Feed */}
      {posts.length > 0 ? (
        <div className="space-y-4 md:space-y-6">
          {posts.map((post) => (
            <Post
              key={post.id}
              post={post}
              uploader={post.uploader}
            />
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="bg-surface rounded-2xl shadow-lg border border-gray-100 p-8 md:p-12">
          <div className="text-center max-w-md mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-accent/20 to-primary/20 flex items-center justify-center">
              <ImageOff className="w-10 h-10 text-primary/60" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Your feed is empty
            </h3>
            <p className="text-gray-600 mb-6">
              Start by uploading your first photo or follow some users to see their posts here!
            </p>
            <button 
              onClick={() => document.querySelector('[data-upload-trigger]')?.click()}
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary to-dark-accent text-white font-semibold rounded-xl hover:shadow-lg transition-all"
            >
              Upload Your First Photo
            </button>
          </div>
        </div>
      )}
    </div>
  );
}