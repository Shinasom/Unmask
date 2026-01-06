# backend/users/services.py

import numpy as np
import cv2
from insightface.app import FaceAnalysis
import logging
import os

logger = logging.getLogger('users')

# Initialize the model ONCE (Global singleton)
# 'buffalo_l' is more accurate and robust for profile pictures.
# providers=['CPUExecutionProvider'] ensures it runs efficiently on your CPU.
# The reliable, crash-proof setting
app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def extract_face_encoding(user):
    """
    Extract and save face encoding from user's profile picture using InsightFace.
    This should be called when a user uploads/updates their profile pic.
    
    Args:
        user: CustomUser instance
        
    Returns:
        bool: True if encoding extracted successfully, False otherwise
    """
    if not user.profile_pic:
        logger.warning(f"User {user.username} has no profile picture")
        user.encoding_status = 'NO_FACE'
        user.save()
        return False
    
    try:
        # 1. Verify file existence before trying to load
        # This allows us to catch the specific "File not found" error logic you had before
        img_path = user.profile_pic.path
        if not os.path.exists(img_path):
            logger.error(f"Profile picture file not found for user {user.username}")
            user.encoding_status = 'ERROR'
            user.save()
            return False

        # 2. Load the profile picture using OpenCV
        img = cv2.imread(img_path)
        
        if img is None:
            # Fallback if cv2 fails to read a file that exists (corrupt, format, etc)
            logger.error(f"Error reading image file for user {user.username}")
            user.encoding_status = 'ERROR'
            user.save()
            return False
        
        # 3. Get faces (InsightFace handles detection & alignment internally)
        faces = app.get(img)
        
        if len(faces) == 0:
            logger.warning(f"No face detected in profile pic for user {user.username}")
            user.encoding_status = 'NO_FACE'
            user.face_encoding = None
            user.save()
            return False
            
        # 4. Handle Multiple Faces (Restoring your original logging logic)
        if len(faces) > 1:
            logger.warning(f"Multiple faces detected for user {user.username}, using first one")
            
        # 5. Sort by size (largest face is likely the user)
        # bbox is [x1, y1, x2, y2], so we calculate area (w * h)
        faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
        
        # 6. Get the embedding of the largest face
        # InsightFace returns a numpy array, we convert to list for JSON storage
        encoding = faces[0].embedding.tolist()
        
        user.face_encoding = encoding
        user.encoding_status = 'SUCCESS'
        user.save()
        
        logger.info(f"Successfully extracted face encoding for user {user.username}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting face encoding for user {user.username}: {str(e)}")
        user.encoding_status = 'ERROR'
        user.save()
        return False


def get_users_with_encodings():
    """
    Get all users who have successfully computed face encodings.
    
    Returns:
        QuerySet: Users with valid face encodings
    """
    from users.models import CustomUser
    return CustomUser.objects.filter(
        encoding_status='SUCCESS',
        face_encoding__isnull=False
    )


def get_face_encodings_dict():
    """
    Get a dictionary mapping user IDs to their face encodings.
    This is optimized for batch face recognition operations.
    
    Returns:
        tuple: (numpy array of encodings, list of user objects)
    """
    users = get_users_with_encodings()
    
    if not users.exists():
        return np.array([]), []
    
    encodings = []
    user_list = []
    
    for user in users:
        try:
            # Convert JSON list back to numpy array
            # Ensure float32 type for optimal InsightFace calculations
            encoding = np.array(user.face_encoding, dtype=np.float32)
            encodings.append(encoding)
            user_list.append(user)
        except Exception as e:
            logger.error(f"Error loading encoding for user {user.username}: {str(e)}")
            continue
    
    return np.array(encodings), user_list


def recompute_all_face_encodings():
    """
    Recompute face encodings for all users with profile pictures.
    Useful for migrations or if encoding algorithm changes.
    
    Returns:
        dict: Statistics about the recomputation
    """
    from users.models import CustomUser
    
    users = CustomUser.objects.exclude(profile_pic__in=['', None])
    
    stats = {
        'total': users.count(),
        'success': 0,
        'no_face': 0,
        'error': 0
    }
    
    for user in users:
        success = extract_face_encoding(user)
        
        if success:
            stats['success'] += 1
        elif user.encoding_status == 'NO_FACE':
            stats['no_face'] += 1
        else:
            stats['error'] += 1
    
    logger.info(f"Face encoding recomputation complete: {stats}")
    return stats