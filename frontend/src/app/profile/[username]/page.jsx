'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { Loader2, Grid3x3, Bookmark, UserSquare2 } from 'lucide-react';
import ProfileHeader from '@/components/profile/ProfileHeader';
import PhotoGrid from '@/components/profile/PhotoGrid';
import FollowersModal from '@/components/profile/FollowersModal';

export default function ProfilePage() {
  const [userProfile, setUserProfile] = useState(null);
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('posts');
  const [isFollowing, setIsFollowing] = useState(false);
  const [followerCount, setFollowerCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  const [showFollowersModal, setShowFollowersModal] = useState(false);
  const [showFollowingModal, setShowFollowingModal] = useState(false);
  
  const params = useParams();
  const router = useRouter();
  const { username } = params;
  const { user: loggedInUser } = useAuth();

  useEffect(() => {
    fetchProfileData();
  }, [username]);

  const fetchProfileData = async () => {
    if (!username) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/api/users/profile/${username}/`);
      setUserProfile(response.data.user);
      setPhotos(response.data.photos || []);

      const userId = response.data.user.id;
      const isOwnProfile = loggedInUser?.username === username;

      if (!isOwnProfile && userId) {
        try {
          const followStatusRes = await api.get(`/api/users/${userId}/follow-status/`);
          setIsFollowing(followStatusRes.data.is_following);
        } catch (err) {
          console.error('Error fetching follow status:', err);
        }
      }

      if (userId) {
        try {
          const countsRes = await api.get(`/api/users/${userId}/follow-counts/`);
          setFollowerCount(countsRes.data.followers_count);
          setFollowingCount(countsRes.data.following_count);
        } catch (err) {
          console.error('Error fetching follow counts:', err);
        }
      }
    } catch (error) {
      console.error("Failed to fetch profile data:", error);
      setUserProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowToggle = async () => {
    if (!userProfile?.id) return;
    
    try {
      const method = isFollowing ? 'delete' : 'post';
      await api[method](`/api/users/${userProfile.id}/follow/`);
      
      setIsFollowing(!isFollowing);
      setFollowerCount(prev => isFollowing ? prev - 1 : prev + 1);
    } catch (err) {
      console.error('Error toggling follow:', err);
    }
  };

  const handlePhotoDelete = (photoId) => {
    setPhotos(prev => prev.filter(photo => photo.id !== photoId));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-[#556B2F]" />
      </div>
    );
  }

  if (!userProfile) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">User Not Found</h1>
        <p className="text-gray-600 mb-4">This user doesn't exist or may have been removed.</p>
        <button
          onClick={() => router.push('/feed')}
          className="px-4 py-2 bg-[#556B2F] text-white rounded-lg hover:bg-[#3A5A40] transition-colors"
        >
          Go to Feed
        </button>
      </div>
    );
  }

  const isOwnProfile = loggedInUser?.username === userProfile.username;

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <div className="max-w-[935px] mx-auto px-4 sm:px-6 py-8">
        <div className="bg-white rounded-lg border border-gray-200 mb-7 p-8">
          <ProfileHeader
            userProfile={userProfile}
            isOwnProfile={isOwnProfile}
            isFollowing={isFollowing}
            followerCount={followerCount}
            followingCount={followingCount}
            postCount={photos.length}
            onFollowToggle={handleFollowToggle}
            onFollowersClick={() => setShowFollowersModal(true)}
            onFollowingClick={() => setShowFollowingModal(true)}
          />
        </div>

        <div className="bg-white rounded-t-lg border-t border-x border-gray-200">
          <div className="flex justify-center border-b border-gray-200">
            <button
              onClick={() => setActiveTab('posts')}
              className={`flex items-center gap-2 px-12 py-3 text-xs font-semibold tracking-wide uppercase transition-colors ${
                activeTab === 'posts'
                  ? 'text-gray-900 border-t-2 border-gray-900 -mt-px'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <Grid3x3 className="w-3 h-3" />
              Posts
            </button>
            
            {isOwnProfile && (
              <>
                <button
                  onClick={() => setActiveTab('saved')}
                  className={`flex items-center gap-2 px-12 py-3 text-xs font-semibold tracking-wide uppercase transition-colors ${
                    activeTab === 'saved'
                      ? 'text-gray-900 border-t-2 border-gray-900 -mt-px'
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <Bookmark className="w-3 h-3" />
                  Saved
                </button>
                
                <button
                  onClick={() => setActiveTab('tagged')}
                  className={`flex items-center gap-2 px-12 py-3 text-xs font-semibold tracking-wide uppercase transition-colors ${
                    activeTab === 'tagged'
                      ? 'text-gray-900 border-t-2 border-gray-900 -mt-px'
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <UserSquare2 className="w-3 h-3" />
                  Tagged
                </button>
              </>
            )}
          </div>
        </div>

        <div className="bg-white rounded-b-lg border-b border-x border-gray-200 p-4">
          {activeTab === 'posts' && (
            <PhotoGrid
              photos={photos}
              isOwnProfile={isOwnProfile}
              onPhotoDelete={handlePhotoDelete}
            />
          )}
          
          {activeTab === 'saved' && (
            <div className="py-16 text-center">
              <Bookmark className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No Saved Posts Yet
              </h3>
              <p className="text-gray-500">
                Posts you save will appear here
              </p>
            </div>
          )}
          
          {activeTab === 'tagged' && (
            <div className="py-16 text-center">
              <UserSquare2 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No Tagged Posts Yet
              </h3>
              <p className="text-gray-500">
                Photos you're tagged in will appear here
              </p>
            </div>
          )}
        </div>
      </div>

      {showFollowersModal && userProfile?.id && (
        <FollowersModal
          userId={userProfile.id}
          type="followers"
          onClose={() => setShowFollowersModal(false)}
        />
      )}

      {showFollowingModal && userProfile?.id && (
        <FollowersModal
          userId={userProfile.id}
          type="following"
          onClose={() => setShowFollowingModal(false)}
        />
      )}
    </div>
  );
}