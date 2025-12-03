# backend/photos/services.py

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image, ImageFilter
from django.core.files import File
import logging
import time
import os

from users.models import CustomUser
from users.services import get_face_encodings_dict
from .models import Photo, ConsentRequest, DetectedFace

logger = logging.getLogger('photos')

# Initialize InsightFace (Global)
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def _regenerate_public_image(photo: Photo):
    """
    Regenerates the public image by applying Gaussian blur to all faces
    that are not unmasked (approved/public/uploader).
    """
    logger.info(f"[Regenerate] START: Regenerating public_image for photo {photo.id}.")
    start_time = time.time()

    try:
        if not photo.original_image or not os.path.exists(photo.original_image.path):
            logger.error(f"[Regenerate] Original image file not found for photo {photo.id}")
            return

        # 1. Load the pristine original image using PIL
        original = Image.open(photo.original_image.path)
        public_image = original.convert('RGB')

        # 2. Get all detected faces from the database
        all_detected_faces = photo.detected_faces.all()
        logger.debug(f"[Regenerate] Photo {photo.id}: Found {len(all_detected_faces)} stored faces in database.")

        if not all_detected_faces:
            logger.warning(f"[Regenerate] Photo {photo.id}: No detected faces found in DB. Image will be public.")
        
        # 3. Get approved user IDs
        approved_users_ids = list(
            photo.consent_requests.filter(status='APPROVED').values_list('requested_user_id', flat=True)
        )
        logger.debug(f"[Regenerate] Photo {photo.id}: Found {len(approved_users_ids)} approved users.")

        # 4. Determine which faces to mask
        faces_to_mask = []
        for face in all_detected_faces:
            unmask_face = False
            
            if face.matched_user:
                # Uploader always sees themselves
                if face.matched_user_id == photo.uploader_id:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (Uploader: {face.matched_user.username}).")
                # Public profile users
                elif face.matched_user.face_sharing_mode == CustomUser.FaceSharingMode.PUBLIC:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (PUBLIC mode: {face.matched_user.username}).")
                # Users who approved the request
                elif face.matched_user_id in approved_users_ids:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (APPROVED: {face.matched_user.username}).")
            
            if not unmask_face:
                faces_to_mask.append(face.bounding_box)
                logger.debug(f"[Regenerate] Photo {photo.id}: Masking face at {face.bounding_box} (User: {face.matched_user or 'Unknown'}).")

        logger.info(f"[Regenerate] Photo {photo.id}: Total={len(all_detected_faces)}, Unmasked={len(all_detected_faces) - len(faces_to_mask)}, Masked={len(faces_to_mask)}.")

        # 5. Apply Gaussian Blur to masked faces
        for bounding_box_str in faces_to_mask:
            try:
                # Parse "left,top,right,bottom"
                coords = [int(float(c)) for c in bounding_box_str.split(',')]
                left, top, right, bottom = coords
                
                # Create box tuple (left, top, right, bottom)
                box = (left, top, right, bottom)
                
                # Validate coordinates
                img_w, img_h = public_image.size
                if left < 0 or top < 0 or right > img_w or bottom > img_h:
                    continue

                # Crop, Blur, Paste
                face_crop = public_image.crop(box)
                blurred_face = face_crop.filter(ImageFilter.GaussianBlur(radius=20))
                public_image.paste(blurred_face, box)
                
            except Exception as e:
                logger.error(f"[Regenerate] Photo {photo.id}: Error parsing or blurring bounding box '{bounding_box_str}': {e}")

        # 6. Save result
        from io import BytesIO
        temp_thumb = BytesIO()
        public_image.save(temp_thumb, format='JPEG', quality=90)
        temp_thumb.seek(0)

        photo.public_image.save(
            f"public_{photo.id}.jpg",
            File(temp_thumb),
            save=True
        )
        temp_thumb.close()

        total_time = time.time() - start_time
        logger.info(f"[Regenerate] SUCCESS: Regenerated public_image for {photo.id} in {total_time:.3f}s.")

    except Exception as e:
        logger.error(f"[Regenerate] FAILED: Error regenerating public_image for {photo.id}: {e}", exc_info=True)


def process_photo_for_faces(photo_id: int):
    """
    Main entry point for processing a new photo using InsightFace.
    """
    start_time = time.time()
    logger.info(f"[PhotoProcessing] START: Processing NEW photo_id {photo_id}...")
    
    try:
        photo = Photo.objects.get(id=photo_id)
        uploader = photo.uploader
    except Photo.DoesNotExist:
        logger.error(f"[PhotoProcessing] FATAL: Photo with id {photo_id} not found.")
        return

    try:
        # 1. Initialize public image (copy original)
        if not photo.original_image or not os.path.exists(photo.original_image.path):
            logger.error(f"[PhotoProcessing] Original image file not found: {photo.original_image.path}")
            return

        photo.public_image.save(
            photo.original_image.name,
            File(photo.original_image.file),
            save=True
        )

        # 2. Load known encodings
        encoding_load_start = time.time()
        known_encodings_array, known_users = get_face_encodings_dict()
        encoding_load_time = time.time() - encoding_load_start
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Loaded {len(known_users)} encodings in {encoding_load_time:.3f}s.")
        
        # 3. Detect faces using InsightFace (Fast!)
        detection_start = time.time()
        img_path = photo.original_image.path
        img = cv2.imread(img_path)
        
        if img is None:
            logger.error(f"[PhotoProcessing] Error reading image file: {img_path}")
            return

        faces = app.get(img)
        detection_time = time.time() - detection_start
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Detected {len(faces)} faces in {detection_time:.3f}s.")

        if len(faces) == 0:
            logger.info(f"[PhotoProcessing] Photo {photo.id}: No faces detected.")
            return

        # 4. Match faces and create DB records
        matching_start = time.time()
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Saving all {len(faces)} detected faces to database...")
        
        found_users_for_consent = set()

        for face in faces:
            # InsightFace bbox is [x1, y1, x2, y2] which translates to [left, top, right, bottom]
            box = face.bbox.astype(int)
            # Store as "left,top,right,bottom"
            bounding_box_str = f"{box[0]},{box[1]},{box[2]},{box[3]}"
            
            matched_user = None
            
            # Fast Matching using Dot Product
            if len(known_users) > 0:
                source_embedding = face.embedding
                # Cosine similarity (dot product of normalized vectors)
                source_norm = source_embedding / np.linalg.norm(source_embedding)
                known_norms = known_encodings_array / np.linalg.norm(known_encodings_array, axis=1, keepdims=True)
                
                scores = np.dot(known_norms, source_norm)
                best_score_index = np.argmax(scores)
                best_score = scores[best_score_index]
                
                # Threshold for InsightFace (usually 0.5 - 0.6)
                if best_score > 0.5:
                    matched_user = known_users[best_score_index]

            # Save DetectedFace
            DetectedFace.objects.create(
                photo=photo,
                bounding_box=bounding_box_str,
                matched_user=matched_user
            )

            # Logic for Consent Requests
            if matched_user:
                is_uploader = matched_user.id == uploader.id
                is_public = matched_user.face_sharing_mode == CustomUser.FaceSharingMode.PUBLIC
                
                if not is_uploader and not is_public and matched_user.id not in found_users_for_consent:
                    ConsentRequest.objects.create(
                        photo=photo,
                        requested_user=matched_user,
                        bounding_box=bounding_box_str
                    )
                    found_users_for_consent.add(matched_user.id)
                    logger.info(f"[PhotoProcessing] Photo {photo.id}: Created ConsentRequest for {matched_user.username}.")

        matching_time = time.time() - matching_start 
        logger.info(f"[PhotoProcessing] Photo {photo.id}: DB save complete in {matching_time:.3f}s. Created {len(found_users_for_consent)} requests.")

        # 5. Apply masking
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Calling _regenerate_public_image to create initial masked version.")
        _regenerate_public_image(photo)

        total_time = time.time() - start_time
        logger.info(f"[PhotoProcessing] SUCCESS: Finished NEW photo {photo.id} in {total_time:.3f}s.")

    except Exception as e:
        logger.error(f"[PhotoProcessing] FAILED: Error processing NEW photo {photo.id}: {e}", exc_info=True)


def unmask_approved_face(consent_request_id: int):
    """
    Called when a user approves a request. Just triggers regeneration.
    """
    logger.info(f"[Unmasking] START: Received approval for consent_request_id {consent_request_id}...")
    try:
        req = ConsentRequest.objects.get(id=consent_request_id)
        if req.status == 'APPROVED':
            logger.info(f"[Unmasking] Request {consent_request_id}: User {req.requested_user.username} approved. Triggering regeneration for photo {req.photo.id}.")
            _regenerate_public_image(req.photo)
            logger.info(f"[Unmasking] SUCCESS: Photo {req.photo.id} regenerated for {req.requested_user.username}.")
        else:
            logger.warning(f"[Unmasking] SKIPPED: Request {consent_request_id} status is '{req.status}', not 'APPROVED'.")
            
    except ConsentRequest.DoesNotExist:
        logger.error(f"[Unmasking] FAILED: ConsentRequest {consent_request_id} not found.")
    except Photo.DoesNotExist:
        logger.error(f"[Unmasking] FAILED: Photo not found for request {consent_request_id}.")
    except Exception as e:
        logger.error(f"[Unmasking] FAILED: An unexpected error occurred for request {consent_request_id}. Error: {e}", exc_info=True)