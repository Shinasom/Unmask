// frontend/src/app/messages/page.jsx
'use client';

import { useState, useEffect, useRef, memo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useChat } from '@/context/ChatContext';
import api from '@/lib/api';
import { 
  MessageCircle, 
  Search, 
  ArrowLeft, 
  Send, 
  Loader2, 
  Plus,
  X,
  Phone,
  Video,
  Info
} from 'lucide-react';

// Helper function to get full image URL
const getFullImageUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('http')) return url;
  return `http://127.0.0.1:8000${url}`;
};

// Memoized Avatar component to prevent re-renders
const Avatar = memo(({ src, alt, size = 'md', className = '' }) => {
  const [imgSrc, setImgSrc] = useState(() => getFullImageUrl(src));
  const [hasError, setHasError] = useState(false);
  
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };
  
  const sizePixels = {
    sm: '32',
    md: '40',
    lg: '48',
  };
  
  const fallbackUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(alt || '?')}&background=556B2F&color=fff&size=${sizePixels[size]}`;
  
  useEffect(() => {
    const newSrc = getFullImageUrl(src);
    if (newSrc !== imgSrc) {
      setImgSrc(newSrc);
      setHasError(false);
    }
  }, [src]);
  
  const handleError = () => {
    if (!hasError) {
      setImgSrc(fallbackUrl);
      setHasError(true);
    }
  };
  
  return (
    <div className={`${sizeClasses[size]} rounded-full overflow-hidden ${className} bg-gray-200`}>
      <img
        src={imgSrc || fallbackUrl}
        alt={alt}
        className="w-full h-full object-cover"
        onError={handleError}
        loading="lazy"
      />
    </div>
  );
});

Avatar.displayName = 'Avatar';

export default function MessagesPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { 
    messages: liveMessages, 
    connectionStatus, 
    sendMessage,
    sendTypingIndicator,
    typingUsers 
  } = useChat();
  
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingMessages, setLoadingMessages] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  // Listen for live messages
  useEffect(() => {
    if (liveMessages.length > 0 && selectedConversation) {
      const latestMessage = liveMessages[liveMessages.length - 1];
      
      if (latestMessage.conversation === selectedConversation.id) {
        setConversationMessages((prev) => {
          const messageExists = prev.some(msg => msg.id === latestMessage.id);
          if (messageExists) return prev;
          return [...prev, latestMessage];
        });
        
        // Update conversation list with last message
        setConversations(prev => 
          prev.map(conv => 
            conv.id === selectedConversation.id 
              ? { ...conv, last_message: latestMessage, last_message_at: latestMessage.created_at }
              : conv
          )
        );
      }
    }
  }, [liveMessages, selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [conversationMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/conversations/');
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (conversation) => {
    setSelectedConversation(conversation);
    setConversationMessages([]);
    setLoadingMessages(true);
    
    try {
      const response = await api.get(`/api/messages/?conversation=${conversation.id}`);
      const messages = response.data.results ? response.data.results.reverse() : [];
      setConversationMessages(messages);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !selectedConversation) return;

    setSendingMessage(true);
    const text = messageText;
    setMessageText('');
    
    const success = sendMessage(selectedConversation.id, text);
    
    if (!success) {
      setMessageText(text);
    }
    
    setSendingMessage(false);
  };

  const handleTyping = (e) => {
    setMessageText(e.target.value);
    
    if (selectedConversation) {
      sendTypingIndicator(selectedConversation.id, e.target.value.length > 0);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.other_participant?.username?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar - Conversations List */}
      <div className={`w-full md:w-96 bg-surface flex flex-col border-r border-gray-100 ${selectedConversation ? 'hidden md:flex' : 'flex'}`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-primary/5 to-accent/5">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
            <button
              onClick={() => setShowNewChatModal(true)}
              className="p-2.5 bg-primary hover:bg-dark-accent text-white rounded-xl transition-all shadow-sm hover:shadow-md"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
            />
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center space-x-2 text-xs mt-3">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
              'bg-red-500'
            }`} />
            <span className="text-gray-600 font-medium capitalize">
              {connectionStatus}
            </span>
          </div>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length > 0 ? (
            <div className="p-2">
              {filteredConversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => selectConversation(conv)}
                  className={`w-full p-3 flex items-center space-x-3 hover:bg-gray-50 transition-all rounded-xl mb-1 group ${
                    selectedConversation?.id === conv.id ? 'bg-primary/10 shadow-sm' : ''
                  }`}
                >
                  <div className="relative">
                    <Avatar
                      src={conv.other_participant?.profile_pic}
                      alt={conv.other_participant?.username}
                      size="lg"
                      className="ring-2 ring-white"
                    />
                    {/* Online indicator */}
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {conv.other_participant?.username}
                      </h3>
                      {conv.last_message?.created_at && (
                        <span className="text-xs text-gray-500">
                          {new Date(conv.last_message.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 truncate">
                      {conv.last_message?.text || 'Start a conversation...'}
                    </p>
                  </div>
                  {conv.unread_count > 0 && (
                    <div className="bg-primary text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">
                      {conv.unread_count}
                    </div>
                  )}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center px-8 py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center mb-4">
                <MessageCircle className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No conversations yet</h3>
              <p className="text-sm text-gray-500 mb-4">
                Start a new conversation to connect with others
              </p>
              <button
                onClick={() => setShowNewChatModal(true)}
                className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-dark-accent transition-colors"
              >
                Start New Chat
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right Side - Chat Window */}
      {selectedConversation ? (
        <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-50 to-white">
          {/* Chat Header */}
          <div className="p-4 bg-surface border-b border-gray-100 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSelectedConversation(null)}
                className="md:hidden p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <Avatar
                src={selectedConversation.other_participant?.profile_pic}
                alt={selectedConversation.other_participant?.username}
                size="md"
                className="ring-2 ring-primary/20"
              />
              <div className="flex-1">
                <h2 className="font-semibold text-gray-900">
                  {selectedConversation.other_participant?.username}
                </h2>
                {typingUsers[selectedConversation.other_participant?.id] ? (
                  <p className="text-sm text-primary">typing...</p>
                ) : (
                  <p className="text-sm text-gray-500">Active now</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <Phone className="w-5 h-5 text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <Video className="w-5 h-5 text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <Info className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {loadingMessages ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : conversationMessages.length > 0 ? (
              conversationMessages.map((msg, index) => {
                const isOwn = msg.sender.id === user.id;
                const showAvatar = !isOwn && (
                  index === conversationMessages.length - 1 ||
                  conversationMessages[index + 1]?.sender.id !== msg.sender.id
                );
                
                return (
                  <div
                    key={msg.id}
                    className={`flex items-end space-x-2 ${isOwn ? 'justify-end' : 'justify-start'}`}
                  >
                    {!isOwn && (
                      <div className="w-8 h-8 flex-shrink-0">
                        {showAvatar && (
                          <Avatar
                            src={msg.sender.profile_pic}
                            alt={msg.sender.username}
                            size="sm"
                          />
                        )}
                      </div>
                    )}
                    
                    <div className={`max-w-xs lg:max-w-md ${isOwn ? 'order-first' : ''}`}>
                      <div
                        className={`px-4 py-2 rounded-2xl ${
                          isOwn
                            ? 'bg-gradient-to-br from-primary to-dark-accent text-white rounded-br-sm'
                            : 'bg-white text-gray-900 shadow-sm rounded-bl-sm'
                        }`}
                      >
                        <p className="text-sm break-words">{msg.text}</p>
                      </div>
                      <p className={`text-xs mt-1 ${isOwn ? 'text-right text-gray-500' : 'text-left text-gray-500'}`}>
                        {new Date(msg.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center mb-4">
                  <MessageCircle className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No messages yet</h3>
                <p className="text-sm text-gray-500">
                  Send a message to start the conversation
                </p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="p-4 bg-surface border-t border-gray-100">
            <div className="flex items-center space-x-3">
              <input
                type="text"
                value={messageText}
                onChange={handleTyping}
                placeholder="Type a message..."
                className="flex-1 px-4 py-3 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-gray-900 transition-all"
                disabled={sendingMessage}
                autoFocus
              />
              <button
                type="submit"
                disabled={!messageText.trim() || sendingMessage}
                className="p-3 bg-gradient-to-br from-primary to-dark-accent text-white rounded-2xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all disabled:hover:shadow-none"
              >
                {sendingMessage ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="hidden md:flex flex-1 items-center justify-center bg-gradient-to-br from-gray-50 to-white">
          <div className="text-center px-8">
            <div className="w-24 h-24 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageCircle className="w-12 h-12 text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Select a conversation</h2>
            <p className="text-gray-600 mb-6">
              Choose a chat from the list or start a new conversation
            </p>
            <button
              onClick={() => setShowNewChatModal(true)}
              className="px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-dark-accent transition-colors shadow-md hover:shadow-lg"
            >
              Start New Chat
            </button>
          </div>
        </div>
      )}

      {/* New Chat Modal */}
      {showNewChatModal && (
        <NewChatModal
          conversations={conversations}
          onClose={() => setShowNewChatModal(false)}
          onSelectUser={(conversation) => {
            setShowNewChatModal(false);
            fetchConversations();
            selectConversation(conversation);
          }}
        />
      )}
    </div>
  );
}

// New Chat Modal Component
function NewChatModal({ conversations, onClose, onSelectUser }) {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [creating, setCreating] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users/');
      // Filter out current user
      const filteredUsers = response.data.filter(u => u.id !== user?.id);
      setUsers(filteredUsers);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async (userId) => {
    setCreating(userId);
    
    // Check if conversation already exists
    const existingConv = conversations.find(conv => 
      conv.other_participant?.id === userId
    );
    
    if (existingConv) {
      // Conversation exists, just select it
      onSelectUser(existingConv);
      return;
    }
    
    // Create new conversation
    try {
      const response = await api.post('/api/conversations/', { user_id: userId });
      onSelectUser(response.data);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      
      // Check if error is because conversation already exists
      if (error.response?.status === 400) {
        // Try to find the conversation in the list
        const conv = conversations.find(c => c.other_participant?.id === userId);
        if (conv) {
          onSelectUser(conv);
        } else {
          alert('This conversation already exists. Please refresh the page.');
        }
      } else {
        alert('Failed to create conversation. Please try again.');
      }
    } finally {
      setCreating(null);
    }
  };

  const filteredUsers = users.filter(u =>
    u.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    `${u.first_name} ${u.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Check if user already has a conversation
  const hasConversation = (userId) => {
    return conversations.some(conv => conv.other_participant?.id === userId);
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50" onClick={onClose} />
      <div className="fixed inset-x-4 top-1/2 -translate-y-1/2 md:inset-x-auto md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-md z-50">
        <div className="bg-surface rounded-2xl shadow-2xl max-h-[80vh] flex flex-col">
          {/* Modal Header */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">New Message</h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                autoFocus
              />
            </div>
          </div>

          {/* Users List */}
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : filteredUsers.length > 0 ? (
              <div className="space-y-2">
                {filteredUsers.map((u) => {
                  const alreadyHasConv = hasConversation(u.id);
                  return (
                    <button
                      key={u.id}
                      onClick={() => handleCreateConversation(u.id)}
                      disabled={creating === u.id}
                      className="w-full p-3 flex items-center space-x-3 hover:bg-gray-50 rounded-xl transition-colors disabled:opacity-50"
                    >
                      <Avatar
                        src={u.profile_pic}
                        alt={u.username}
                        size="md"
                        className="ring-2 ring-white"
                      />
                      <div className="flex-1 text-left">
                        <div className="flex items-center space-x-2">
                          <p className="font-semibold text-gray-900">{u.username}</p>
                          {alreadyHasConv && (
                            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                              Chat exists
                            </span>
                          )}
                        </div>
                        {u.first_name && (
                          <p className="text-sm text-gray-500">{u.first_name} {u.last_name}</p>
                        )}
                      </div>
                      {creating === u.id ? (
                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      ) : (
                        <div className="text-xs text-gray-400">
                          {alreadyHasConv ? 'View' : 'Chat'}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No users found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}