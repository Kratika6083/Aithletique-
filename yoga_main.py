# Yoga_main.py

import cv2
import random
from pose_detection.mediapipe_model import PoseDetector
from backend.feedback_engine.yoga_feedback_engine import get_feedback_tags, feedback_lines
from voice.tts_engine import speak

# Initialize detector
detector = PoseDetector()

# Open webcam
cap = cv2.VideoCapture(0)

print("Press 'q' to quit.")
spoken_tags = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect pose and draw landmarks
    results = detector.detect_pose(frame)
    frame = detector.draw_landmarks(frame, results)
    landmarks = detector.get_named_landmarks(results)

    if landmarks:
        tags = get_feedback_tags(landmarks)

        for tag in tags:
            if tag not in spoken_tags:  # Prevent repeating
                message = random.choice(feedback_lines.get(tag, []))
                print(f"Feedback: {message}")
                speak(message)
                spoken_tags.add(tag)

        if "pose_correct" in tags:
            spoken_tags.clear()  # Reset if user corrects the pose

    cv2.imshow("Yoga Feedback", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
