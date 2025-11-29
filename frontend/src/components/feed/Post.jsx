// =======================================================================
// /src/components/feed/Post.jsx
// UPDATED: Added clickable uploader profile navigation
// =======================================================================
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MoreHorizontal, Heart, MessageCircle, Send, Bookmark } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import CommentModal from './CommentModal';

export default function Post({ post, uploader }) {
  const { user } = useAuth();
  const router = useRouter();
  const [likes, setLikes] = useState(post.likes || []);
  const [comments, setComments] = useState(post.comments || []);
  const [isCommentModalOpen, setCommentModalOpen] = useState(false);

  if (!post || !post.public_image || !uploader) {
    return null;
  }

  const hasLiked = likes.some(like => like.user.id === user.id);

  const handleLike = async () => {
    if (hasLiked) {
      const like = likes.find(like => like.user.id === user.id);
      await api.delete(`/api/likes/${like.id}/`);
      setLikes(likes.filter(l => l.id !== like.id));
    } else {
      const response = await api.post('/api/likes/', { photo: post.id });
      setLikes([...likes, response.data]);
    }
  };

  const handleCommentAdded = (newComment) => {
    setComments([...comments, newComment]);
  };

  const handleProfileClick = () => {
    router.push(`/profile/${uploader.username}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <>
      <article className="bg-surface rounded-xl md:rounded-2xl shadow-md border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow">
        {/* Post Header */}
        <div className="flex items-center justify-between p-3 md:p-4">
          <div className="flex items-center space-x-2 md:space-x-3">
            <img 
              src={uploader.profile_pic} 
              alt={uploader.username} 
              onClick={handleProfileClick}
              className="w-9 h-9 md:w-10 md:h-10 rounded-full object-cover ring-2 ring-primary/20 cursor-pointer hover:ring-primary/40 transition-all"
              onError={(e) => { 
                e.target.onerror = null; 
                e.target.src = `https://placehold.co/40x40/556B2F/FFFFFF?text=${uploader.username?.charAt(0).toUpperCase() || 'U'}`; 
              }}
            />
            <div>
              <p 
                onClick={handleProfileClick}
                className="font-semibold text-sm text-gray-900 hover:text-primary cursor-pointer transition-colors"
              >
                {uploader.username}
              </p>
              <p className="text-xs text-gray-500">
                {formatDate(post.created_at)}
              </p>
            </div>
          </div>
          <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
            <MoreHorizontal className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Post Image */}
        <div className="relative w-full bg-gray-100">
          <img 
            src={post.public_image} 
            alt={post.caption || 'A photo by ' + uploader.username} 
            className="w-full h-auto object-contain max-h-[500px] md:max-h-[600px]"
            onError={(e) => { 
              e.target.onerror = null; 
              e.target.src = 'https://placehold.co/800x600/eee/ccc?text=Image+Not+Available'; 
            }}
          />
        </div>

        {/* Post Actions */}
        <div className="p-3 md:p-4 space-y-2 md:space-y-3">
          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 md:space-x-4">
              <button 
                onClick={handleLike}
                className="p-1 md:p-2 -ml-1 md:-ml-2 rounded-full hover:bg-gray-100 transition-colors group"
              >
                <Heart 
                  className={`w-6 h-6 md:w-7 md:h-7 transition-all ${
                    hasLiked 
                      ? 'text-red-500 fill-red-500 scale-110' 
                      : 'text-gray-600 group-hover:text-red-500 group-hover:scale-110'
                  }`}
                  strokeWidth={2}
                />
              </button>
              <button 
                onClick={() => setCommentModalOpen(true)}
                className="p-1 md:p-2 rounded-full hover:bg-gray-100 transition-colors group"
              >
                <MessageCircle 
                  className="w-6 h-6 md:w-7 md:h-7 text-gray-600 group-hover:text-primary group-hover:scale-110 transition-all" 
                  strokeWidth={2}
                />
              </button>
              <button className="p-1 md:p-2 rounded-full hover:bg-gray-100 transition-colors group">
                <Send 
                  className="w-6 h-6 md:w-7 md:h-7 text-gray-600 group-hover:text-primary group-hover:scale-110 transition-all" 
                  strokeWidth={2}
                />
              </button>
            </div>
            <button className="p-1 md:p-2 rounded-full hover:bg-gray-100 transition-colors group">
              <Bookmark 
                className="w-6 h-6 md:w-7 md:h-7 text-gray-600 group-hover:text-primary group-hover:scale-110 transition-all" 
                strokeWidth={2}
              />
            </button>
          </div>

          {/* Likes Count */}
          {likes.length > 0 && (
            <div className="flex items-center space-x-2">
              {likes.length === 1 ? (
                <p className="text-sm">
                  <span className="font-semibold text-gray-900">
                    {likes[0].user.username}
                  </span>
                  <span className="text-gray-600"> liked this</span>
                </p>
              ) : (
                <p className="text-sm font-semibold text-gray-900">
                  {likes.length.toLocaleString()} likes
                </p>
              )}
            </div>
          )}

          {/* Caption */}
          {post.caption && (
            <div className="text-sm">
              <span 
                onClick={handleProfileClick}
                className="font-semibold text-gray-900 mr-2 hover:text-primary cursor-pointer transition-colors"
              >
                {uploader.username}
              </span>
              <span className="text-gray-700">{post.caption}</span>
            </div>
          )}

          {/* Comments Preview */}
          {comments.length > 0 && (
            <div className="space-y-1 md:space-y-2">
              {comments.length > 2 && (
                <button 
                  onClick={() => setCommentModalOpen(true)}
                  className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
                >
                  View all {comments.length} comments
                </button>
              )}
              
              {comments.slice(0, 2).map(comment => (
                <div key={comment.id} className="text-sm">
                  <span className="font-semibold text-gray-900 mr-2">
                    {comment.user.username}
                  </span>
                  <span className="text-gray-700">{comment.text}</span>
                </div>
              ))}
            </div>
          )}

          {/* Add Comment */}
          <button 
            onClick={() => setCommentModalOpen(true)}
            className="w-full text-left text-sm text-gray-400 hover:text-gray-600 transition-colors pt-2 border-t border-gray-100"
          >
            Add a comment...
          </button>
        </div>
      </article>

      {/* Comment Modal */}
      {isCommentModalOpen && (
        <CommentModal
          post={post}
          onClose={() => setCommentModalOpen(false)}
          onCommentAdded={handleCommentAdded}
        />
      )}
    </>
  );
}