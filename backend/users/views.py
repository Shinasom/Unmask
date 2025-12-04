# backend/users/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Follow
from photos.models import Photo
from .services import extract_face_encoding  # Import the encoding service

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
    ViewSet for user management with a built-in follow system.
    This handles Registration, Profiles, Following, and Face Encodings.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    # We remove the class-level permission_classes to use get_permissions instead
    # permission_classes = [IsAuthenticated] 

    def get_permissions(self):
        """
        Custom permission logic:
        - Allow ANYONE (anonymous users) to access 'create' (Registration).
        - Require AUTHENTICATION for all other actions (Profile, Follow, etc.).
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Hook that runs during user registration (POST /api/users/).
        
        1. Save the user instance (Django handles password hashing).
        2. If a profile picture was uploaded, IMMEDIATELY generate the 
           face encoding so the user can be recognized in photos right away.
        """
        user = serializer.save()
        if user.profile_pic:
            logger.info(f"Generating initial face encoding for new user: {user.username}")
            # This calls our optimized InsightFace service
            extract_face_encoding(user)

    @action(
        detail=False, 
        methods=['get'], 
        url_path='profile/(?P<username>[^/.]+)',
        permission_classes=[IsAuthenticated]
    )
    def profile(self, request, username=None):
        """
        Custom endpoint to fetch a full user profile.
        URL: /api/users/profile/<username>/
        
        Returns:
            - user: The user's details (bio, profile pic, etc.)
            - photos: A list of photos uploaded by this user.
        """
        try:
            # 1. Fetch the user object by username
            user = CustomUser.objects.get(username=username)
            
            # 2. Fetch their photos, ordered by newest first
            photos = Photo.objects.filter(uploader=user).order_by('-created_at')
            
            # 3. Serialize the data into JSON format
            user_data = UserSerializer(user).data
            # Use the photo serializer if available, otherwise return empty list
            photos_data = PhotoSerializer(photos, many=True).data if PhotoSerializer else []
            
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
        Toggle follow status for a user.
        
        POST: Follow the user.
        DELETE: Unfollow the user.
        """
        target_user = self.get_object() # The user we want to follow/unfollow
        current_user = request.user     # The user currently logged in
        
        # Security Check: Prevent users from following themselves
        if target_user == current_user:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'POST':
            # Create the follow relationship if it doesn't exist
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
            # Remove the follow relationship
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
        Helper endpoint to check if I am following this user.
        Used by the frontend to toggle the "Follow/Unfollow" button state.
        """
        target_user = self.get_object()
        
        # Check existence of the relationship
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=target_user
        ).exists()
        
        return Response({'is_following': is_following})
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def follow_counts(self, request, pk=None):
        """
        Return the social stats for a user.
        - followers_count: How many people follow them.
        - following_count: How many people they follow.
        """
        user = self.get_object()
        
        return Response({
            'followers_count': Follow.objects.filter(following=user).count(),
            'following_count': Follow.objects.filter(follower=user).count()
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        """
        Get the list of people who follow this user.
        Uses select_related for database optimization.
        """
        user = self.get_object()
        
        # 1. Query the Follow table
        follow_relationships = Follow.objects.filter(following=user).select_related('follower')
        
        # 2. Extract the actual User objects from the relationships
        followers_list = [rel.follower for rel in follow_relationships]
        
        # 3. Serialize the list of users
        serializer = UserSerializer(followers_list, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        """
        Get the list of people this user follows.
        """
        user = self.get_object()
        
        # 1. Query the Follow table
        follow_relationships = Follow.objects.filter(follower=user).select_related('following')
        
        # 2. Extract the actual User objects
        following_list = [rel.following for rel in follow_relationships]
        
        # 3. Serialize
        serializer = UserSerializer(following_list, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def recompute_encoding(self, request, pk=None):
        """
        Admin/Debug Action: Force re-calculation of a user's face encoding.
        Useful if the user changed their photo or if we switched AI models (Dlib -> InsightFace).
        """
        user = self.get_object()
        
        # Security: Only allow the user themselves or an Admin to do this
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Run the extraction service
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