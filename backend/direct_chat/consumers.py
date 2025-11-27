# backend/direct_chat/consumers.py
"""
WebSocket consumer for real-time chat messaging.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message
from .serializers import MessageSerializer
import logging

logger = logging.getLogger('direct_chat')


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat messages.
    
    Connection URL: ws://localhost:8000/ws/chat/?token=<jwt_token>
    
    Message format (client → server):
    {
        "type": "chat_message",
        "conversation_id": 1,
        "text": "Hello!"
    }
    
    Message format (server → client):
    {
        "type": "chat_message",
        "message": {
            "id": 123,
            "conversation": 1,
            "sender": {...},
            "text": "Hello!",
            "created_at": "2025-01-15T10:30:00Z"
        }
    }
    """
    
    async def connect(self):
        """
        Called when WebSocket connection is established.
        """
        self.user = self.scope['user']
        
        # Reject anonymous users
        if self.user.is_anonymous:
            logger.warning("Anonymous user attempted WebSocket connection")
            await self.close(code=4001)
            return
        
        # Accept the connection
        await self.accept()
        logger.info(f"WebSocket connected: {self.user.username}")
        
        # Join all conversation groups for this user
        conversations = await self.get_user_conversations()
        for conversation in conversations:
            group_name = f"chat_{conversation.id}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            logger.debug(f"{self.user.username} joined group: {group_name}")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat server'
        }))
    
    async def disconnect(self, close_code):
        """
        Called when WebSocket connection is closed.
        """
        if hasattr(self, 'user') and not self.user.is_anonymous:
            # Leave all conversation groups
            conversations = await self.get_user_conversations()
            for conversation in conversations:
                group_name = f"chat_{conversation.id}"
                await self.channel_layer.group_discard(group_name, self.channel_name)
            
            logger.info(f"WebSocket disconnected: {self.user.username} (code: {close_code})")
    
    async def receive(self, text_data):
        """
        Called when a message is received from the client.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from {self.user.username}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def handle_chat_message(self, data):
        """
        Handle incoming chat message: save to DB and broadcast to group.
        """
        conversation_id = data.get('conversation_id')
        text = data.get('text', '').strip()
        
        if not conversation_id or not text:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'conversation_id and text are required'
            }))
            return
        
        # Verify user is a participant
        is_participant = await self.verify_participant(conversation_id)
        if not is_participant:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You are not a participant in this conversation'
            }))
            return
        
        # Save message to database
        message = await self.save_message(conversation_id, text)
        
        if message:
            # Serialize message
            message_data = await self.serialize_message(message)
            
            # Broadcast to conversation group
            group_name = f"chat_{conversation_id}"
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': message_data
                }
            )
            
            logger.info(f"Message {message.id} sent by {self.user.username} to conversation {conversation_id}")
    
    async def handle_typing_indicator(self, data):
        """
        Handle typing indicator: broadcast to group (don't save to DB).
        """
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        if not conversation_id:
            return
        
        # Verify user is a participant
        is_participant = await self.verify_participant(conversation_id)
        if not is_participant:
            return
        
        # Broadcast typing indicator
        group_name = f"chat_{conversation_id}"
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'typing_indicator_broadcast',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_mark_read(self, data):
        """
        Handle marking messages as read.
        """
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return
        
        # Mark messages as read
        updated_count = await self.mark_messages_read(conversation_id)
        
        await self.send(text_data=json.dumps({
            'type': 'messages_marked_read',
            'conversation_id': conversation_id,
            'count': updated_count
        }))
    
    async def chat_message_broadcast(self, event):
        """
        Called when a message is broadcast to the group.
        Send it to the WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing_indicator_broadcast(self, event):
        """
        Called when a typing indicator is broadcast to the group.
        """
        # Don't send typing indicator back to the sender
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    # Database operations (sync functions wrapped with database_sync_to_async)
    
    @database_sync_to_async
    def get_user_conversations(self):
        """Get all conversations for the current user."""
        return list(self.user.conversations.all())
    
    @database_sync_to_async
    def verify_participant(self, conversation_id):
        """Verify user is a participant in the conversation."""
        return Conversation.objects.filter(
            id=conversation_id,
            participants=self.user
        ).exists()
    
    @database_sync_to_async
    def save_message(self, conversation_id, text):
        """Save message to database and update conversation timestamp."""
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=self.user
            )
            
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                text=text
            )
            
            # Update conversation's last_message_at
            conversation.last_message_at = message.created_at
            conversation.save(update_fields=['last_message_at'])
            
            return message
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {conversation_id} not found for user {self.user.username}")
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message object."""
        serializer = MessageSerializer(message)
        return serializer.data
    
    @database_sync_to_async
    def mark_messages_read(self, conversation_id):
        """Mark all unread messages in a conversation as read."""
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=self.user
            )
            
            updated = conversation.messages.filter(
                is_read=False
            ).exclude(
                sender=self.user
            ).update(is_read=True)
            
            return updated
        except Conversation.DoesNotExist:
            return 0