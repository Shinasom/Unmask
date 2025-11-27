# backend/direct_chat/views.py
from django.db import models  # Add this at the top
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Max
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationCreateSerializer,
    MessageSerializer
)
from users.models import CustomUser
import logging

logger = logging.getLogger('direct_chat')


class MessagePagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    list: Get all conversations for the current user
    create: Create a new conversation with another user
    retrieve: Get a specific conversation
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return conversations for the current user"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')
    
    def create(self, request, *args, **kwargs):
        """
        Create or retrieve a conversation with another user.
        Expects: { "user_id": 123 }
        """
        serializer = ConversationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        other_user_id = serializer.validated_data['user_id']
        other_user = CustomUser.objects.get(id=other_user_id)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).annotate(
            participant_count=models.Count('participants')
        ).filter(
            participant_count=2
        ).first()
        
        if existing_conversation:
            logger.info(f"Found existing conversation {existing_conversation.id}")
            serializer = ConversationSerializer(
                existing_conversation,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        
        logger.info(f"Created new conversation {conversation.id} between {request.user.username} and {other_user.username}")
        
        serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark all messages in a conversation as read"""
        conversation = self.get_object()
        updated = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)
        
        return Response({
            'status': 'success',
            'messages_marked': updated
        })


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    
    list: Get all messages for a conversation (requires ?conversation=<id>)
    create: Send a new message (via WebSocket is preferred)
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        """
        Return messages for a specific conversation.
        Requires ?conversation=<id> query parameter.
        """
        conversation_id = self.request.query_params.get('conversation')
        
        if not conversation_id:
            return Message.objects.none()
        
        # Verify user is a participant
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=self.request.user
            )
        except Conversation.DoesNotExist:
            return Message.objects.none()
        
        return Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message (HTTP fallback).
        WebSocket is the preferred method.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data['conversation'].id
        
        # Verify user is a participant
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found or you are not a participant'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Save message
        message = serializer.save(sender=request.user)
        
        # Update conversation timestamp
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=['last_message_at'])
        
        logger.info(f"Message {message.id} created via HTTP by {request.user.username}")
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )