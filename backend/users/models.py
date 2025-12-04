# backend/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class Follow(models.Model):
    """Model to track user follow relationships"""
    follower = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='following_set',
        help_text='The user who is following'
    )
    following = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='follower_set',
        help_text='The user being followed'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['following', '-created_at']),
            models.Index(fields=['follower', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class CustomUser(AbstractUser):
    """
    Our custom user model with face encoding support for optimized face recognition.
    """
    
    class FaceSharingMode(models.TextChoices):
        REQUIRE_CONSENT = 'REQUIRE_CONSENT', 'Require Consent'
        PUBLIC = 'PUBLIC', 'Public (Auto-unmask)'
    
    # Profile fields
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Face recognition fields
    face_encoding = models.JSONField(
        null=True, 
        blank=True, 
        help_text="128-dimensional face encoding vector"
    )
    
    encoding_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SUCCESS', 'Success'),
            ('NO_FACE', 'No Face Found'),
            ('ERROR', 'Error'),
        ],
        default='PENDING',
        help_text="Status of face encoding extraction"
    )

    # Privacy preference
    face_sharing_mode = models.CharField(
        max_length=20,
        choices=FaceSharingMode.choices,
        default=FaceSharingMode.REQUIRE_CONSENT,
        help_text="User's preference for face sharing"
    )
    
    # Fix for groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username
    
    def has_valid_face_encoding(self):
        """Check if user has a successfully computed face encoding."""
        return self.encoding_status == 'SUCCESS' and self.face_encoding is not None