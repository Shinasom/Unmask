# backend/photos/services.py (FINAL OPTIMIZED VERSION - WITH GAUSSIAN BLUR)

import face_recognition
import numpy as np
# Import ImageFilter for Gaussian Blur
from PIL import Image, ImageDraw, ImageFilter
from django.core.files import File
from django.db.models import Q
import logging
import time

from users.models import CustomUser
from users.services import get_face_encodings_dict
# Import the new DetectedFace model
from .models import Photo, ConsentRequest, DetectedFace

logger = logging.getLogger('photos')


def _regenerate_public_image(photo: Photo):
    """
    This is the "source of truth" function, optimized to use the DetectedFace table.
    UPDATED: Now uses Gaussian Blur instead of a black box.
    """
    logger.info(f"[Regenerate] START: Regenerating public_image for photo {photo.id}.")
    start_time = time.time()

    try:
        # 1. Load the pristine original image
        original = Image.open(photo.original_image.path)
        public_image = original.convert('RGB')
        # We no longer need ImageDraw
        # draw = ImageDraw.Draw(public_image)

        # 2. Get all detected faces *from the database*
        all_detected_faces = photo.detected_faces.all()
        logger.debug(f"[Regenerate] Photo {photo.id}: Found {len(all_detected_faces)} stored faces in database.")

        if not all_detected_faces:
            logger.warning(f"[Regenerate] Photo {photo.id}: No detected faces found in DB. Image will be public.")
        
        # 3. Get all *approved* consent requests for this photo
        approved_users_ids = list(
            photo.consent_requests.filter(status='APPROVED').values_list('requested_user_id', flat=True)
        )
        logger.debug(f"[Regenerate] Photo {photo.id}: Found {len(approved_users_ids)} approved users.")

        # 4. Loop through all stored faces and decide which to mask
        faces_to_mask = []
        for face in all_detected_faces:
            unmask_face = False
            
            # 4a. Check if the face belongs to a matched user
            if face.matched_user:
                # 4a.i. Is it the uploader?
                if face.matched_user_id == photo.uploader_id:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (Uploader: {face.matched_user.username}).")
                
                # 4a.ii. Is it a 'PUBLIC' user?
                elif face.matched_user.face_sharing_mode == CustomUser.FaceSharingMode.PUBLIC:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (PUBLIC mode: {face.matched_user.username}).")
                
                # 4a.iii. Is it an 'APPROVED' request?
                elif face.matched_user_id in approved_users_ids:
                    unmask_face = True
                    logger.debug(f"[Regenerate] Photo {photo.id}: Unmasking face at {face.bounding_box} (APPROVED: {face.matched_user.username}).")
            
            # 4b. If no unmask rule matched, it must be masked
            if not unmask_face:
                faces_to_mask.append(face.bounding_box)
                logger.debug(f"[Regenerate] Photo {photo.id}: Masking face at {face.bounding_box} (User: {face.matched_user or 'Unknown'}).")

        logger.info(f"[Regenerate] Photo {photo.id}: Total={len(all_detected_faces)}, Unmasked={len(all_detected_faces) - len(faces_to_mask)}, Masked={len(faces_to_mask)}.")

        # --- STEP 5: (NEW) Apply Gaussian Blur to all faces that need masking ---
        for bounding_box_str in faces_to_mask:
            try:
                coords = [int(c) for c in bounding_box_str.split(',')]
                left, top, right, bottom = coords
                
                # Create the box tuple (left, top, right, bottom)
                box = (left, top, right, bottom)
                
                # Crop the face region
                face_crop = public_image.crop(box)
                
                # Apply a strong Gaussian blur
                # We can adjust the radius later if we want it stronger or weaker
                blurred_face = face_crop.filter(ImageFilter.GaussianBlur(radius=20))
                
                # Paste the blurred face back into the main image
                public_image.paste(blurred_face, box)
                
            except Exception as e:
                logger.error(f"[Regenerate] Photo {photo.id}: Error parsing or blurring bounding box '{bounding_box_str}': {e}")

        # del draw (No longer need this)
        # --- END OF NEW STEP 5 ---

        # 6. Save the final image to the public_image field
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
    Service function to perform face recognition on *newly uploaded* photos.
    This function now:
    1. Runs detection ONCE.
    2. Populates the new `DetectedFace` table with ALL faces.
    3. Creates `ConsentRequest` objects for matched users who require it.
    4. Calls `_regenerate_public_image()` to build the initial masked version.
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
        # --- Step 1: Create the initial public image (as a pristine copy) ---
        photo.public_image.save(
            photo.original_image.name,
            File(photo.original_image.file),
            save=True
        )

        # --- Step 2: Load pre-computed user encodings ---
        encoding_load_start = time.time()
        known_encodings_array, known_users = get_face_encodings_dict()
        encoding_load_time = time.time() - encoding_load_start
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Loaded {len(known_users)} encodings in {encoding_load_time:.3f}s.")
        
        # --- Step 3: Detect faces in the uploaded photo (RUNS ONCE) ---
        detection_start = time.time()
        original_image_path = photo.original_image.path
        unknown_image = face_recognition.load_image_file(original_image_path)
        unknown_face_locations = face_recognition.face_locations(unknown_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image, unknown_face_locations)
        detection_time = time.time() - detection_start
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Detected {len(unknown_face_locations)} faces in {detection_time:.3f}s.")

        if len(unknown_face_locations) == 0:
            logger.info(f"[PhotoProcessing] Photo {photo.id}: No faces detected.")
            return

        # --- Step 4: Save ALL faces to DB and Create Consent Requests ---
        matching_start = time.time()
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Saving all {len(unknown_face_locations)} detected faces to database...")
        
        found_users_for_consent = set()
        
        for unknown_encoding, face_location in zip(unknown_face_encodings, unknown_face_locations):
            top, right, bottom, left = face_location
            bounding_box_str = f"{left},{top},{right},{bottom}"
            matched_user = None # Default to unknown

            # Try to match the face
            if len(known_users) > 0:
                matches = face_recognition.compare_faces(known_encodings_array, unknown_encoding, tolerance=0.6)
                if True in matches:
                    matched_user = known_users[matches.index(True)]

            # Save this face to the new DetectedFace table
            DetectedFace.objects.create(
                photo=photo,
                bounding_box=bounding_box_str,
                matched_user=matched_user
            )

            # If we found a user, check if they need a consent request
            if matched_user:
                is_uploader = matched_user.id == uploader.id
                is_public = matched_user.face_sharing_mode == CustomUser.FaceSharingMode.PUBLIC
                
                # Only create a request if they are not the uploader, not public,
                # and we haven't already made a request for them for this photo.
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
        
        # --- Step 5: Call the regeneration function ---
        logger.info(f"[PhotoProcessing] Photo {photo.id}: Calling _regenerate_public_image to create initial masked version.")
        _regenerate_public_image(photo)

        total_time = time.time() - start_time
        logger.info(f"[PhotoProcessing] SUCCESS: Finished NEW photo {photo.id} in {total_time:.3f}s.")

    except Exception as e:
        logger.error(f"[PhotoProcessing] FAILED: Error processing NEW photo {photo.id}: {e}", exc_info=True)


def unmask_approved_face(consent_request_id: int):
    """
    Service to unmask a single approved face on the public image.
    This function now just calls the regeneration function.
    """
    logger.info(f"[Unmasking] START: Received approval for consent_request_id {consent_request_id}...")
    
    try:
        consent_request = ConsentRequest.objects.get(id=consent_request_id)
        
        if consent_request.status != 'APPROVED':
            logger.warning(f"[Unmasking] SKIPPED: Request {consent_request_id} status is '{consent_request.status}', not 'APPROVED'.")
            return

        photo = consent_request.photo
        user = consent_request.requested_user
        logger.info(f"[Unmasking] Request {consent_request_id}: User {user.username} approved. Triggering regeneration for photo {photo.id}.")
        
        # --- NEW LOGIC ---
        # Call the ultra-fast regeneration function. No face detection needed!
        _regenerate_public_image(photo)
        
        logger.info(f"[Unmasking] SUCCESS: Photo {photo.id} regenerated for {user.username}.")

    except ConsentRequest.DoesNotExist:
        logger.error(f"[Unmasking] FAILED: ConsentRequest {consent_request_id} not found.")
    except Photo.DoesNotExist:
        logger.error(f"[Unmasking] FAILED: Photo not found for request {consent_request_id}.")
    except Exception as e:
        logger.error(f"[Unmasking] FAILED: An unexpected error occurred for request {consent_request_id}. Error: {e}", exc_info=True)

