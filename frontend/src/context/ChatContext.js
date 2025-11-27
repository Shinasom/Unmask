// frontend/src/context/ChatContext.js
'use client';

import { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const { user } = useAuth();
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [typingUsers, setTypingUsers] = useState({});
  const reconnectTimeoutRef = useRef(null);

  // Connect WebSocket when user is authenticated
  useEffect(() => {
    if (!user) {
      setConnectionStatus('disconnected');
      return;
    }

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [user]);

  const connectWebSocket = () => {
    // Get token from localStorage (same way your api.js does it)
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      console.error('No access token found');
      setConnectionStatus('disconnected');
      return;
    }

    console.log('🔌 Connecting WebSocket with token:', token.substring(0, 20) + '...');
    setConnectionStatus('connecting');

    const ws = new WebSocket(
      `ws://127.0.0.1:8000/ws/chat/?token=${token}`
    );

    ws.onopen = () => {
      console.log('✅ WebSocket Connected');
      setConnectionStatus('connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 WebSocket message:', data);

      switch (data.type) {
        case 'connection_established':
          console.log('✅ Connection established:', data.message);
          break;

        case 'chat_message':
          // Add new message to state
          setMessages((prev) => [...prev, data.message]);
          break;

        case 'typing_indicator':
          handleTypingIndicator(data);
          break;

        case 'messages_marked_read':
          console.log('✓ Messages marked as read:', data);
          break;

        case 'error':
          console.error('WebSocket error:', data.message);
          break;

        default:
          console.log('Unknown message type:', data);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnectionStatus('error');
    };

    ws.onclose = (event) => {
      console.log('🔌 WebSocket closed:', event.code, event.reason);
      setConnectionStatus('disconnected');
      setSocket(null);

      // Auto-reconnect after 3 seconds (except for authentication failures)
      if (event.code !== 1000 && event.code !== 4001) {
        console.log('🔄 Attempting to reconnect in 3s...');
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      } else if (event.code === 4001) {
        console.error('❌ Authentication failed - token may be expired');
      }
    };
  };

  const handleTypingIndicator = (data) => {
    const { user_id, username, is_typing } = data;

    if (is_typing) {
      setTypingUsers((prev) => ({
        ...prev,
        [user_id]: username,
      }));

      // Auto-remove after 3 seconds
      setTimeout(() => {
        setTypingUsers((prev) => {
          const updated = { ...prev };
          delete updated[user_id];
          return updated;
        });
      }, 3000);
    } else {
      setTypingUsers((prev) => {
        const updated = { ...prev };
        delete updated[user_id];
        return updated;
      });
    }
  };

  const sendMessage = (conversationId, text) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return false;
    }

    const message = {
      type: 'chat_message',
      conversation_id: conversationId,
      text: text,
    };

    socket.send(JSON.stringify(message));
    return true;
  };

  const sendTypingIndicator = (conversationId, isTyping) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(
      JSON.stringify({
        type: 'typing',
        conversation_id: conversationId,
        is_typing: isTyping,
      })
    );
  };

  const markAsRead = (conversationId) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(
      JSON.stringify({
        type: 'mark_read',
        conversation_id: conversationId,
      })
    );
  };

  const contextValue = {
    socket,
    messages,
    setMessages,
    conversations,
    setConversations,
    connectionStatus,
    typingUsers,
    sendMessage,
    sendTypingIndicator,
    markAsRead,
    reconnect: connectWebSocket,
  };

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};