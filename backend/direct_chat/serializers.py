# backend/direct_chat/serializers.py
from rest_framework import serializers
from .models import Conversation, Message
from users.models import CustomUser

class MessageSenderSerializer(serializers.ModelSerializer):
    """Minimal user info for message sender"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_pic']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = MessageSenderSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Minimal user info for conversation participants"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_pic']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 
            'participants', 
            'other_participant',
            'last_message', 
            'unread_count',
            'created_at', 
            'last_message_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']
    
    def get_last_message(self, obj):
        last_msg = obj.messages.first()  # Already ordered by -created_at
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()
    
    def get_other_participant(self, obj):
        user = self.context['request'].user
        other = obj.get_other_participant(user)
        if other:
            return ConversationParticipantSerializer(other).data
        return None


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer for creating a conversation"""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        try:
            user = CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        # Can't create conversation with yourself
        if user == self.context['request'].user:
            raise serializers.ValidationError("Cannot create conversation with yourself.")
        
        return value