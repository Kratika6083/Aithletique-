import time
import streamlit as st
import numpy as np
import threading
from backend.feedback_engine.pose_comparator import (
    generate_directional_feedback,
    generate_advanced_feedback,
    check_enough_landmarks
)

JOINT_NAMES = {
     11: 'right shoulder', 12: 'left shoulder', 13: 'right elbow', 14: 'left elbow',
    15: 'right wrist', 16: 'left wrist', 23: 'right hip', 24: 'left hip',
    25: 'right knee', 26: 'left knee', 27: 'right ankle', 28: 'left ankle'
}

POSE_DELAY = 3

speak_lock = threading.Lock()

def async_speak(coach, text):
    def speak_in_thread():
        with speak_lock:
            try:
                coach.speak(text)
            except Exception as e:
                print(f"[Voice Thread ERROR] {e}")

    threading.Thread(target=speak_in_thread, daemon=True).start()

def should_give_feedback(key, delay=3):
    now = time.time()
    last = st.session_state.feedback_timers.get(key, 0)
    if now - last > delay:
        st.session_state.feedback_timers[key] = now
        return True
    return False

def draw_feedback_overlay(landmarks, ref_landmarks, joint_names, threshold=0.02):
    import cv2
    wrong_joints = []
    for i, (user, ref) in enumerate(zip(landmarks, ref_landmarks)):
        if i in joint_names:
            ux, uy = user[:2]
            rx, ry = ref[:2]
            if abs(ux - rx) > threshold or abs(uy - ry) > threshold:
                wrong_joints.append((int(ux * 640), int(uy * 480)))
    overlay = np.zeros((480, 640, 3), dtype=np.uint8)
    for x, y in wrong_joints:
        cv2.circle(overlay, (x, y), 8, (0, 0, 255), -1)
    return overlay

def vrikshasana_coach(landmarks, reference, coach):
    if "pose_stage" not in st.session_state:
        st.session_state.pose_stage = 0
    if "last_feedback_time" not in st.session_state:
        st.session_state.last_feedback_time = 0
    if "last_feedback_text" not in st.session_state:
        st.session_state.last_feedback_text = ""
    if "start_delay" not in st.session_state:
        st.session_state.start_delay = time.time()
    if "feedback_timers" not in st.session_state:
        st.session_state.feedback_timers = {}

    now = time.time()

    if now - st.session_state.start_delay < 2:
        return

    if not check_enough_landmarks(landmarks):
        return

    left_foot = landmarks[28][1]
    right_knee = landmarks[25][1]
    left_hand = landmarks[15][1]
    right_hand = landmarks[16][1]

    foot_placed = abs(left_foot - right_knee) < 0.1
    hands_joined = abs(left_hand - right_hand) < 0.05

    if "foot_correct" not in st.session_state:
        st.session_state.foot_correct = False
    if "hands_correct" not in st.session_state:
        st.session_state.hands_correct = False

    st.session_state.foot_correct = foot_placed
    st.session_state.hands_correct = hands_joined

    feedback_given = False

    if not foot_placed:
        if should_give_feedback("foot", delay=POSE_DELAY):
            async_speak(coach, "Raise your left foot and place it on your right thigh.")
            st.session_state.last_feedback_text = "Raise your left foot and place it on your right thigh."
            feedback_given = True

    if not hands_joined:
        if should_give_feedback("hands", delay=POSE_DELAY):
            async_speak(coach, "Join your hands in front of your chest.")
            st.session_state.last_feedback_text = "Join your hands in front of your chest."
            feedback_given = True

    if feedback_given:
        return

    if st.session_state.foot_correct and st.session_state.hands_correct:
        if st.session_state.pose_stage < 2:
            st.session_state.pose_stage = 2
            st.session_state.last_feedback_text = ""

    if st.session_state.pose_stage == 2:
        if not check_enough_landmarks(landmarks):
            return

        if hasattr(reference, "shape") and reference.ndim == 3:
            ref_pose = reference[0]
        else:
            ref_pose = reference

        simple_feedbacks = generate_directional_feedback(landmarks, ref_pose, JOINT_NAMES, threshold=0.015)
        advanced_feedbacks = generate_advanced_feedback(landmarks, ref_pose, JOINT_NAMES, angle_threshold=10)
        combined_feedbacks = simple_feedbacks + advanced_feedbacks

        st.session_state.overlay = draw_feedback_overlay(landmarks, ref_pose, JOINT_NAMES)

        if combined_feedbacks:
            current_feedback = combined_feedbacks[0]
            feedback_changed = current_feedback != st.session_state.last_feedback_text
            if should_give_feedback("pose_correction", delay=POSE_DELAY) or feedback_changed:
                async_speak(coach, current_feedback)
                st.session_state.last_feedback_text = current_feedback
        else:
            st.session_state.last_feedback_text = ""

    if not foot_placed or not hands_joined:
        st.session_state.pose_stage = 1
