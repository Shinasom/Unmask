# backend/users/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Follow
from photos.models import Photo
# Import whatever serializer name you actually have
# Try both common patterns:
try:
    from .serializers import UserSerializer
except ImportError:
    from .serializers import CustomUserSerializer as UserSerializer

try:
    from photos.serializers import PhotoSerializer
except ImportError:
    # If PhotoSerializer doesn't exist, we'll create a simple dict response
    PhotoSerializer = None

import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management with follow system.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(
        detail=False, 
        methods=['get'], 
        url_path='profile/(?P<username>[^/.]+)',
        permission_classes=[IsAuthenticated]  # CRITICAL: This was missing!
    )
    def profile(self, request, username=None):
        """
        Get a user's profile and their photos.
        
        Returns:
            - user: User object
            - photos: List of user's photos
        """
        try:
            # Get the user
            user = CustomUser.objects.get(username=username)
            
            # Get their photos (ordered by most recent)
            photos = Photo.objects.filter(uploader=user).order_by('-created_at')
            # Serialize the data
            user_data = UserSerializer(user).data
            photos_data = PhotoSerializer(photos, many=True).data
            
            logger.info(f"Profile fetched: {username} by {request.user.username}")
            
            return Response({
                'user': user_data,
                'photos': photos_data
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            logger.warning(f"Profile not found: {username}")
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """
        Follow or unfollow a user.
        
        POST: Follow a user
        DELETE: Unfollow a user
        """
        target_user = self.get_object()
        current_user = request.user
        
        # Prevent self-follow
        if target_user == current_user:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'POST':
            # Create follow relationship
            follow, created = Follow.objects.get_or_create(
                follower=current_user,
                following=target_user
            )
            
            if created:
                logger.info(f"{current_user.username} followed {target_user.username}")
                return Response(
                    {'message': f'Successfully followed {target_user.username}'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': f'Already following {target_user.username}'},
                    status=status.HTTP_200_OK
                )
        
        elif request.method == 'DELETE':
            # Remove follow relationship
            deleted_count, _ = Follow.objects.filter(
                follower=current_user,
                following=target_user
            ).delete()
            
            if deleted_count > 0:
                logger.info(f"{current_user.username} unfollowed {target_user.username}")
                return Response(
                    {'message': f'Successfully unfollowed {target_user.username}'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'message': f'Not following {target_user.username}'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def follow_status(self, request, pk=None):
        """
        Check if the current user is following this user.
        
        Returns:
            {"is_following": true/false}
        """
        target_user = self.get_object()
        current_user = request.user
        
        is_following = Follow.objects.filter(
            follower=current_user,
            following=target_user
        ).exists()
        
        return Response({'is_following': is_following})
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def follow_counts(self, request, pk=None):
        """
        Get follower and following counts for a user.
        
        Returns:
            {
                "followers_count": int,
                "following_count": int
            }
        """
        user = self.get_object()
        
        followers_count = Follow.objects.filter(following=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        
        return Response({
            'followers_count': followers_count,
            'following_count': following_count
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        """
        Get list of users following this user.
        
        Returns list of user objects.
        """
        user = self.get_object()
        
        # Get all follower relationships
        follow_relationships = Follow.objects.filter(following=user).select_related('follower')
        
        # Extract follower users
        followers = [rel.follower for rel in follow_relationships]
        
        # Serialize
        serializer = UserSerializer(followers, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        """
        Get list of users this user is following.
        
        Returns list of user objects.
        """
        user = self.get_object()
        
        # Get all following relationships
        follow_relationships = Follow.objects.filter(follower=user).select_related('following')
        
        # Extract following users
        following = [rel.following for rel in follow_relationships]
        
        # Serialize
        serializer = UserSerializer(following, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def recompute_encoding(self, request, pk=None):
        """
        Recompute face encoding for a user.
        Admin or self only.
        """
        user = self.get_object()
        
        # Only allow self or admin
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Import here to avoid circular dependency
        from .services import extract_face_encoding
        
        success = extract_face_encoding(user)
        
        if success:
            return Response({
                'message': 'Face encoding recomputed successfully',
                'encoding_status': user.encoding_status
            })
        else:
            return Response({
                'error': 'Failed to recompute face encoding',
                'encoding_status': user.encoding_status
            }, status=status.HTTP_400_BAD_REQUEST)