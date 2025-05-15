import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import cv2
import numpy as np
from backend.pose_detection.mediapipe_model import PoseDetector

pose_folder = "pose_references"
video_folder = "workout_videos"

os.makedirs(pose_folder, exist_ok=True)

model = PoseDetector()

def extract_average_pose(video_path, save_path):
    cap = cv2.VideoCapture(video_path)
    all_landmarks = []
    total_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1
        results = model.detect_pose(frame)
        landmarks = model.get_landmarks(results)
        if landmarks:
            landmarks = [lm[:3] for lm in landmarks]
            flat = np.array(landmarks).flatten()
            all_landmarks.append(flat)

    cap.release()
    if all_landmarks:
        avg_pose = np.mean(all_landmarks, axis=0)
        np.save(save_path, avg_pose)
        print(f"✅ Saved reference pose to {save_path}")
    else:
        print("❌ No valid landmarks found in video.")

    print(f"Processed {total_frames} frames, valid pose frames: {len(all_landmarks)}\n")

# Automatically process all *_correct.mp4 workout videos
for file in os.listdir(video_folder):
    if file.endswith("_correct.mp4"):
        name = file.replace("_correct.mp4", "").lower()
        video_path = os.path.join(video_folder, file)
        save_path = os.path.join(pose_folder, f"{name}_reference.npy")
        print(f"⏳ Processing {file}...")
        extract_average_pose(video_path, save_path)
