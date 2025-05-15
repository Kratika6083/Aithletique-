import cv2
import mediapipe as mp

video_path = "squat.mp4"
cap = cv2.VideoCapture(video_path)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
valid_frames = 0
total_frames = 0

while cap.isOpened() and total_frames < 10:
    ret, frame = cap.read()
    if not ret:
        break
    results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        valid_frames += 1
    total_frames += 1

cap.release()
pose.close()

print(f"Valid pose frames: {valid_frames}/{total_frames}")
