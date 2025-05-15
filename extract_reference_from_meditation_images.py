# extract_reference_from_meditation_images.py
import cv2
import os
import numpy as np
from backend.pose_detection.mediapipe_model import PoseDetector

pose_detector = PoseDetector()

meditation_folder = "Dataset/Meditation"
all_landmarks = []

for file in os.listdir(meditation_folder):
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(meditation_folder, file)
        image = cv2.imread(img_path)
        if image is None:
            continue

        results = pose_detector.detect_pose(image)
        landmarks = pose_detector.get_landmarks(results)
        if landmarks:
            # Flatten the (x, y) coordinates
            flat = np.array(landmarks).flatten()
            all_landmarks.append(flat)

if all_landmarks:
    all_landmarks = np.array(all_landmarks)
    mean_pose = np.mean(all_landmarks, axis=0)
    np.savez("reference_meditation_pose.npz", mean_pose=mean_pose)
    print("✅ Reference meditation pose saved to reference_meditation_pose.npz")
else:
    print("❌ No valid pose landmarks found in the images.")
