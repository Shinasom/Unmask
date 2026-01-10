import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis

def warmup():
    print("🔥 Warming up GPU...")
    # Initialize the app exactly how your server does
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    
    # Run a dummy inference on a tiny black square
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    app.get(dummy_img)
    print("✅ GPU is Hot and Ready!")

if __name__ == "__main__":
    warmup()