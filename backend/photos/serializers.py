from rest_framework import serializers
from .models import Photo, ConsentRequest
from users.models import CustomUser
# Import the new serializers from the interactions app
from interactions.serializers import LikeSerializer, CommentSerializer

# --- NESTED SERIALIZERS ---
# These are small, read-only serializers to represent related objects.

class UploaderInfoSerializer(serializers.ModelSerializer):
    """A simple serializer for displaying uploader info."""
    class Meta:
        model = CustomUser
        fields = ['username', 'profile_pic']

class NestedPhotoSerializer(serializers.ModelSerializer):
    """A simple serializer for displaying photo info within a consent request."""
    uploader = UploaderInfoSerializer(read_only=True)
    class Meta:
        model = Photo
        fields = ['id', 'public_image', 'uploader']


# --- MAIN SERIALIZERS ---

class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for the main Photo model.
    This version includes nested serializers for likes and comments.
    """
    # Instead of a simple username, we'll show the full uploader object
    uploader = UploaderInfoSerializer(read_only=True)
    # These lines will include a list of all like/comment objects for each photo
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        # Add 'likes' and 'comments' to the fields list
        fields = [
            'id', 'uploader', 'public_image', 'original_image',
            'caption', 'created_at', 'likes', 'comments'
        ]
        read_only_fields = ['id', 'created_at', 'public_image', 'likes', 'comments']
        extra_kwargs = {
            'original_image': {'write_only': True, 'required': True}
        }


class ConsentRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the ConsentRequest model.
    This version includes the nested photo object.
    """
    photo = NestedPhotoSerializer(read_only=True)

    class Meta:
        model = ConsentRequest
        fields = [
            'id',
            'photo', # This will now be a rich object.
            'requested_user',
            'status',
            'bounding_box',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'photo', 'requested_user', 'bounding_box', 
            'created_at', 'updated_at'
        ]
