# backend/photos/models.py
from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile # For saving memory-buffer as file
from PIL import Image
import io
import os

class Photo(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='uploaded_photos'
    )
    original_image = models.ImageField(upload_to='photos/originals/%Y/%m/%d/')
    public_image = models.ImageField(upload_to='photos/public/%Y/%m/%d/', null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Optimizes the image by resizing to a max of 2000px and 
        compressing it before saving.
        """
        if self.original_image:
            # 1. Open the image
            img = Image.open(self.original_image)
            
            # Convert to RGB if it's RGBA (transparency can cause JPEG errors)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 2. Resize only if larger than 2000px
            max_size = 3000
            if img.width > max_size or img.height > max_size:
                # thumbnail() maintains the aspect ratio automatically
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # 3. Save the result to a memory buffer
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90, optimize=True)
            
            # 4. Overwrite the original_image field with the optimized version
            file_name = os.path.basename(self.original_image.name)
            self.original_image.save(
                file_name, 
                ContentFile(buffer.getvalue()), 
                save=False
            )
    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo by {self.uploader.username} on {self.created_at.strftime('%Y-%m-%d')}"

class ConsentRequest(models.Model):
    """
    Replaces the old 'noti' model. This is the core of our app's logic.
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        DENIED = 'DENIED', 'Denied'

    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='consent_requests')
    requested_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='consent_requests_received'
    )
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    bounding_box = models.CharField(max_length=100) # To store the face location 'left,top,right,bottom'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request for {self.requested_user.username} on photo {self.photo.id} is {self.status}"


# --- NEW MODEL ---
# This model stores the location of EVERY face detected in a photo,
# not just those requiring consent. This allows us to avoid re-running face detection.
class DetectedFace(models.Model):
    photo = models.ForeignKey(
        Photo, 
        on_delete=models.CASCADE, 
        related_name='detected_faces'
    )
    # Store the coordinates 'left,top,right,bottom'
    bounding_box = models.CharField(max_length=100) 
    
    # Link to the matched user, if any.
    # If the user is deleted, the face just becomes "Unknown"
    matched_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='faces_detected_in_photos'
    )

    def __str__(self):
        user_str = self.matched_user.username if self.matched_user else "Unknown"
        return f"Face ({user_str}) in Photo {self.photo.id} at {self.bounding_box}"