// frontend/src/components/profile/ProfileHeader.jsx
"use client";

import { Settings, UserPlus, UserCheck } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ProfileHeader({
  userProfile,
  isOwnProfile,
  isFollowing,
  followerCount,
  followingCount,
  postCount,
  onFollowToggle,
  onFollowersClick,
  onFollowingClick,
}) {
  const router = useRouter();

  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith("http")) return path;
    return `http://127.0.0.1:8000${path}`;
  };

  const getAvatarUrl = () => {
    const profilePicUrl = getImageUrl(userProfile?.profile_pic);
    if (profilePicUrl) return profilePicUrl;
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(
      userProfile?.username || "User"
    )}&size=150&background=556B2F&color=fff&bold=true`;
  };

  return (
    <div className="flex flex-col md:flex-row gap-8 md:gap-12">
      {/* Avatar */}
      <div className="flex justify-center md:justify-start flex-shrink-0">
        <div className="relative">
          <img
            src={getAvatarUrl()}
            alt={userProfile?.username}
            className="w-[150px] h-[150px] rounded-full object-cover border-2 border-gray-200"
            onError={(e) => {
              e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(
                userProfile?.username || "User"
              )}&size=150&background=556B2F&color=fff&bold=true`;
            }}
          />
          {/* Online indicator (optional) */}
          {isOwnProfile && (
            <div className="absolute bottom-2 right-2 w-6 h-6 bg-green-500 rounded-full border-4 border-white"></div>
          )}
        </div>
      </div>

      {/* Profile Info */}
      <div className="flex-1 min-w-0">
        {/* Username and Action Button Row */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-5">
          <h1 className="text-2xl font-light text-gray-900 break-words">
            {userProfile?.username}
          </h1>

          <div className="flex gap-2">
            {isOwnProfile ? (
              <>
                <button
                  onClick={() => router.push("/settings/profile")}
                  className="flex items-center gap-2 px-6 py-1.5 text-sm font-semibold text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Edit profile
                </button>
                <button
                  onClick={() => router.push("/settings")}
                  className="px-3 py-1.5 text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  aria-label="Settings"
                >
                  <Settings className="w-5 h-5" />
                </button>
              </>
            ) : (
              <button
                onClick={onFollowToggle}
                className={`flex items-center gap-2 px-8 py-1.5 text-sm font-semibold rounded-lg transition-all ${
                  isFollowing
                    ? "text-gray-900 bg-white border border-gray-300 hover:bg-gray-50"
                    : "text-white bg-[#0095F6] hover:bg-[#0082D9]"
                }`}
              >
                {isFollowing ? (
                  <>
                    <UserCheck className="w-4 h-4" />
                    Following
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    Follow
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-8 mb-5">
          <div className="flex gap-1">
            <span className="font-semibold text-gray-900">{postCount}</span>
            <span className="text-gray-500">posts</span>
          </div>
          
          <button
            onClick={onFollowersClick}
            className="flex gap-1 hover:text-gray-500 transition-colors"
          >
            <span className="font-semibold text-gray-900">{followerCount}</span>
            <span className="text-gray-500">followers</span>
          </button>
          
          <button
            onClick={onFollowingClick}
            className="flex gap-1 hover:text-gray-500 transition-colors"
          >
            <span className="font-semibold text-gray-900">{followingCount}</span>
            <span className="text-gray-500">following</span>
          </button>
        </div>

        {/* Bio */}
        {userProfile?.bio && (
          <div className="text-sm">
            <p className="text-gray-900 whitespace-pre-wrap break-words">
              {userProfile.bio}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}