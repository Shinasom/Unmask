// =======================================================================
// /src/components/shell/Header.jsx
// UPDATED: Added working user search functionality
// =======================================================================
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, User } from 'lucide-react';
import api from '@/lib/api';

export default function Header() {
  const router = useRouter();
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const controlNavbar = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY < 10) {
        setIsVisible(true);
      } else if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false);
        setIsSearchFocused(false);
      } else {
        setIsVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', controlNavbar);
    return () => window.removeEventListener('scroll', controlNavbar);
  }, [lastScrollY]);

  // Search users as user types
  useEffect(() => {
    const searchUsers = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const response = await api.get('/api/users/');
        const filtered = response.data.filter(user =>
          user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (user.first_name && user.first_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (user.last_name && user.last_name.toLowerCase().includes(searchQuery.toLowerCase()))
        );
        setSearchResults(filtered.slice(0, 10)); // Limit to 10 results
      } catch (error) {
        console.error('Search failed:', error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    const debounceTimer = setTimeout(searchUsers, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);

  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleUserClick = (username) => {
    router.push(`/profile/${username}`);
    setSearchQuery('');
    setSearchResults([]);
    setIsSearchFocused(false);
  };

  const getAvatarUrl = (user) => {
    if (user.profile_pic) {
      if (user.profile_pic.startsWith('http')) return user.profile_pic;
      return `http://127.0.0.1:8000${user.profile_pic}`;
    }
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=556B2F&color=fff&size=40`;
  };

  return (
    <header 
      className={`bg-surface/95 backdrop-blur-md shadow-sm fixed top-0 left-0 right-0 md:left-64 lg:right-80 z-20 border-b border-gray-200 transition-transform duration-300 ${
        isVisible ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      <div className="h-16 px-4 sm:px-6 lg:px-8">
        <div className="h-full flex items-center justify-center">
          <div className="w-full max-w-2xl">
            <div className="relative group">
              {/* Search Icon */}
              <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                isSearchFocused ? 'text-primary' : 'text-gray-400'
              }`}>
                <Search className="w-5 h-5 pointer-events-none" />
              </div>

              {/* Search Input */}
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
                placeholder="Search users..."
                className={`w-full bg-gray-50 border-2 focus:outline-none rounded-full pl-12 pr-12 py-3 text-sm text-gray-700 placeholder:text-gray-400 transition-all duration-200 ${
                  isSearchFocused 
                    ? 'border-primary bg-white shadow-lg shadow-primary/10' 
                    : 'border-transparent hover:bg-gray-100 hover:border-gray-200'
                }`}
              />

              {/* Clear Button */}
              {searchQuery && (
                <button
                  onClick={handleClearSearch}
                  className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              )}

              {/* Search Results Dropdown */}
              {isSearchFocused && searchQuery && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-gray-200 py-2 max-h-96 overflow-y-auto">
                  {isSearching ? (
                    <div className="px-4 py-8 text-center">
                      <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <p className="text-sm text-gray-500">Searching...</p>
                    </div>
                  ) : searchResults.length > 0 ? (
                    <div className="px-2">
                      <p className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        Users
                      </p>
                      {searchResults.map(user => (
                        <SearchResultItem
                          key={user.id}
                          user={user}
                          onClick={() => handleUserClick(user.username)}
                          avatarUrl={getAvatarUrl(user)}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="px-4 py-8 text-center">
                      <User className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">No users found</p>
                      <p className="text-xs text-gray-400 mt-1">Try searching for a different username</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

// Search Result Item Component
const SearchResultItem = ({ user, onClick, avatarUrl }) => {
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
  
  return (
    <button 
      onClick={onClick}
      className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 transition-colors group"
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <img 
          src={avatarUrl} 
          alt={user.username}
          className="w-10 h-10 rounded-full object-cover ring-2 ring-gray-100 group-hover:ring-primary/30 transition-all"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=556B2F&color=fff&size=40`;
          }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 text-left min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate group-hover:text-primary transition-colors">
          {user.username}
        </p>
        {fullName && (
          <p className="text-xs text-gray-500 truncate">
            {fullName}
          </p>
        )}
      </div>

      {/* Arrow */}
      <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </button>
  );
};