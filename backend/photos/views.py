from rest_framework import viewsets, permissions
from .models import Photo, ConsentRequest
from .serializers import PhotoSerializer, ConsentRequestSerializer
from . import services

class PhotoViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update`, and `destroy` actions for Photos.
    """
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return photos ordered by newest first, with optimized queries
        """
        return Photo.objects.select_related('uploader').prefetch_related(
            'likes__user',
            'comments__user'
        ).order_by('-created_at')  # Newest first!

    def perform_create(self, serializer):
        """
        This method is a hook that runs when a new photo is created via the API.
        We are overriding it to:
        1. Automatically set the uploader to the currently logged-in user.
        2. Trigger our facial recognition service.
        
        NOTE: The serializer is already configured to handle the 'original_image'
        field from the request, so we just need to save it.
        """
        # First, save the photo instance. The serializer handles saving the
        # 'original_image' and the uploader is set from the request.
        photo_instance = serializer.save(uploader=self.request.user)
        
        # Now, call our service function with the new photo's ID
        services.process_photo_for_faces(photo_id=photo_instance.id)


class ConsentRequestViewSet(viewsets.ModelViewSet):
    """
    This viewset allows a user to view and action their consent requests.
    """
    serializer_class = ConsentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This is a crucial security feature.
        This view should only return a list of all the consent requests
        for the currently authenticated user. It overrides the default
        behavior of showing all objects.
        """
        user = self.request.user
        return ConsentRequest.objects.filter(requested_user=user).order_by('-created_at')

    def perform_update(self, serializer):
        """
        This is a new method added to trigger the unmasking service.
        This hook runs when a consent request is updated (e.g., PATCH request).
        """
        # First, save the instance to ensure the status is updated in the database.
        instance = serializer.save()

        # After saving, check if the new status is 'APPROVED'.
        if instance.status == 'APPROVED':
            # If it is, call our new service to perform the unmasking.
            services.unmask_approved_face(consent_request_id=instance.id)