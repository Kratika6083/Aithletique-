import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
import streamlit as st
import time
from backend.pose_detection.mediapipe_model import PoseDetector
from backend.feedback_engine.workout_feedback import WorkoutFeedback
from backend.feedback_engine.workout_rep_counter import WorkoutRepCounter
from backend.feedback_engine.pose_similarity_checker import compare_pose
from backend.feedback_engine.angles import calculate_angle_from_landmarks

logging.basicConfig(level=logging.INFO)

def start_squat_workout():
    stframe = st.empty()
    rep_placeholder = st.empty()
    similarity_placeholder = st.empty()
    message_placeholder = st.empty()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Unable to access the camera.")
        return

    stop_button = st.button("🛑 Stop Workout")

    model = PoseDetector()
    feedback = WorkoutFeedback()
    rep_counter = WorkoutRepCounter("squat", threshold_down=90, threshold_up=170)

    reference_pose_path = "pose_references/squat_reference.npy"
    angle_reference_path = "pose_references/squat_angles_reference.npy"

    try:
        reference_pose = np.load(reference_pose_path)
        angle_reference_data = np.load(angle_reference_path, allow_pickle=True)
    except FileNotFoundError as e:
        st.error(f"Missing reference file: {e}")
        return

    reps = 0
    similarity = 0.0
    smooth_similarity = []
    similarity_scores = []
    mistakes = []
    last_feedback_time = 0
    cooldown = 3.0
    visibility_threshold = 0.5
    frame_index = 0

    while cap.isOpened():
        if stop_button:
            break

        ret, frame = cap.read()
        if not ret:
            break

        results = model.detect_pose(frame)
        landmarks_full = model.get_landmarks(results)

        if not landmarks_full or any(lm[3] < visibility_threshold for lm in landmarks_full):
            similarity = 0.0
            if time.time() - last_feedback_time > cooldown:
                feedback.give_feedback("pose not fully visible")
                last_feedback_time = time.time()
            message_placeholder.markdown("<span style='color:red'><b>⚠️ Pose not fully visible</b></span>", unsafe_allow_html=True)
            stframe.image(frame, channels="BGR")
            rep_placeholder.markdown(f"### 🏋️ Repetitions: **{reps}**")
            similarity_placeholder.progress(0, text=f"🎯 Accuracy: --")
            time.sleep(0.02)
            continue

        landmarks = [lm[:3] for lm in landmarks_full]
        flat_landmarks = np.array(landmarks).flatten()

        hip_angle = calculate_angle_from_landmarks(landmarks_full, 23, 25, 27)
        back_angle = calculate_angle_from_landmarks(landmarks_full, 11, 23, 24)
        knee_angle = calculate_angle_from_landmarks(landmarks_full, 25, 27, 29)
        leg_gap = np.linalg.norm(np.array(landmarks[27]) - np.array(landmarks[28]))

        deep_position = hip_angle < 90

        if deep_position:
            similarity_now, is_correct = compare_pose(flat_landmarks, reference_pose, threshold=0.92)
            smooth_similarity.append(similarity_now)
            if len(smooth_similarity) > 5:
                smooth_similarity.pop(0)
            similarity = np.mean(smooth_similarity)

            if frame_index < len(angle_reference_data):
                ref_angles = angle_reference_data[frame_index]
                if hip_angle > ref_angles.get("hip", 90) + 15:
                    feedback.give_feedback("bend your knees more")
                    mistakes.append("Knee not bent enough")
                if back_angle < 160:
                    feedback.give_feedback("keep your spine straight")
                    mistakes.append("Spine not straight")
                if leg_gap < 0.1:
                    feedback.give_feedback("keep feet slightly apart")
                    mistakes.append("Feet too close")
                last_feedback_time = time.time()
        else:
            similarity = 0.0
            smooth_similarity.clear()

        if rep_counter.update(hip_angle):
            reps += 1
            if smooth_similarity:
                similarity_scores.append(np.mean(smooth_similarity))
                avg_angle_accuracy = similarity_scores[-1]
                if avg_angle_accuracy < 0.85:
                    feedback.give_feedback("Try to improve your form")
            smooth_similarity.clear()

        frame = model.draw_landmarks(frame, results)
        stframe.image(frame, channels="BGR")
        rep_placeholder.markdown(f"### 🏋️ Repetitions: **{reps}**")
        similarity_placeholder.progress(int(similarity * 100), text=f"🎯 Accuracy: {similarity * 100:.1f}%")
        frame_index += 1
        time.sleep(0.02)

    cap.release()
    st.success("Workout session ended.")
    st.markdown("---")
    st.markdown(f"## 🧾 Squat Session Summary")
    st.markdown(f"**Total Repetitions:** {reps}")
    if similarity_scores:
        st.markdown(f"**Best Accuracy:** {max(similarity_scores) * 100:.1f}%")
        st.markdown(f"**Average Accuracy:** {np.mean(similarity_scores) * 100:.1f}%")
    else:
        st.markdown("**Accuracy Data:** No valid reps captured")

    if mistakes:
        st.markdown("### 🔁 Corrections to Focus On:")
        for issue in set(mistakes):
            st.markdown(f"- {issue}")
