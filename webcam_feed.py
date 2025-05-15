import cv2
import tempfile
import streamlit as st
import time
import numpy as np
import os

from backend.pose_detection.mediapipe_model import PoseDetector
from backend.feedback_engine.vrikshasana_coach import vrikshasana_coach


from backend.feedback_engine.pose_comparator import (
    load_single_reference_landmarks,
    compute_pose_accuracy,
    check_enough_landmarks,
    generate_directional_feedback,
    generate_advanced_feedback
)
from backend.feedback_engine.motion_tools import load_motion_reference, compute_motion_similarity
from backend.voice.tts_engine import VoiceCoach
from database.logger import init_db, log_session

def run_pose_detection(pose_name="tadasana", category="Yoga & Meditation"):
    init_db()

    if "running" not in st.session_state:
        st.session_state.running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "feedback_collected" not in st.session_state:
        st.session_state.feedback_collected = set()
    if "stop" not in st.session_state:
        st.session_state.stop = False
    if "reps" not in st.session_state:
        st.session_state.reps = 0
    if "pose_held" not in st.session_state:
        st.session_state.pose_held = False

    detector = PoseDetector()
    coach = VoiceCoach()

    reference_landmarks = None
    motion_reference = None

    if category == "Yoga & Meditation":
        try:
            corrected_pose_name = pose_name.capitalize()
            reference_landmarks = load_single_reference_landmarks(f"pose_references/{corrected_pose_name}.npz")
        except Exception as e:
            st.error(f"❌ Could not load reference for {pose_name}.")
            return
    elif category == "Workout & Training":
        motion_reference = load_motion_reference(f"motion_references/{pose_name}_motion.npz")
        if motion_reference is None:
            st.error(f"❌ No motion reference found for {pose_name}.")
            return

    st.session_state.running = True
    st.session_state.start_time = time.time()
    st.session_state.feedback_collected = set()
    st.session_state.stop = False
    st.session_state.reps = 0
    st.session_state.pose_held = False
    st.success("✅ Session started. Your form will now be monitored...")

    stop_button_placeholder = st.empty()

    if stop_button_placeholder.button("🔚 Stop Session", key=f"stop_button_once_{pose_name}"):
        st.session_state.stop = True

    process_camera(pose_name, detector, coach, reference_landmarks, motion_reference, stop_button_placeholder)

def process_camera(pose_name, detector, coach, reference_landmarks, motion_reference, stop_button_placeholder):
    camera = cv2.VideoCapture(0)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    stframe = st.empty()
    feedback_placeholder = st.empty()
    accuracy_display = st.empty()
    reps_display = st.empty()

    last_accuracy = 0
    motion_buffer = []

    while camera.isOpened():
        if st.session_state.stop:
            break

        ret, frame = camera.read()
        if not ret:
            st.error("❌ Camera error.")
            break

        frame = cv2.flip(frame, 1)
        results = detector.detect_pose(frame)
        frame = detector.draw_landmarks(frame, results)
        landmarks = detector.get_landmarks(results)

        if landmarks:
            if not check_enough_landmarks(landmarks):
                feedback_placeholder.warning("⚠️ Full body not detected. Please adjust your position!")
                accuracy_display.metric("🎯 Accuracy", "0%")
            else:
                if reference_landmarks is not None:
                    accuracy = compute_pose_accuracy(landmarks, reference_landmarks)
                    last_accuracy = (0.7 * last_accuracy) + (0.3 * accuracy)
                    accuracy_display.metric("🎯 Accuracy", f"{last_accuracy:.2f}%")

                    if last_accuracy >= 90:
                        feedback_placeholder.success("✅ Excellent posture!")
                    elif last_accuracy >= 75:
                        feedback_placeholder.warning("⚠️ Minor Adjustments Needed!")
                    else:
                        feedback_placeholder.error("❌ Major correction needed.")

                    if "last_voice_feedback_time" not in st.session_state:
                        st.session_state.last_voice_feedback_time = 0
                    if "last_feedback_text" not in st.session_state:
                        st.session_state.last_feedback_text = ""

                    now = time.time()
                    feedback_delay = 3

                    if hasattr(reference_landmarks, "shape") and reference_landmarks.ndim == 3:
                        ref = reference_landmarks[np.random.randint(len(reference_landmarks))]
                    else:
                        ref = reference_landmarks

                    JOINT_NAMES = {
                        0: 'nose', 11: 'right shoulder', 12: 'left shoulder', 13: 'right elbow', 14: 'left elbow',
                        15: 'right wrist', 16: 'left wrist', 23: 'right hip', 24: 'left hip',
                        25: 'right knee', 26: 'left knee', 27: 'right ankle', 28: 'left ankle'
                    }

                    # Specific logic for vrikshasana startup check
                    if pose_name.lower() == "vrikshasana":
                        
                        vrikshasana_coach(landmarks, reference_landmarks, coach)

                    else:
                        simple_feedbacks = generate_directional_feedback(landmarks, ref, JOINT_NAMES, threshold=0.015)
                        advanced_feedbacks = generate_advanced_feedback(landmarks, ref, JOINT_NAMES, angle_threshold=10)
                        combined_feedbacks = simple_feedbacks + advanced_feedbacks

                        if combined_feedbacks:
                            current_feedback = combined_feedbacks[0]
                            feedback_changed = current_feedback != st.session_state.last_feedback_text
                            enough_time_passed = (now - st.session_state.last_voice_feedback_time) > feedback_delay

                            if feedback_changed or enough_time_passed:
                                coach.speak(current_feedback)
                                st.session_state.last_feedback_text = current_feedback
                                st.session_state.last_voice_feedback_time = now
                        else:
                            st.session_state.last_feedback_text = ""

                elif motion_reference is not None:
                    motion_buffer.append(landmarks)
                    if len(motion_buffer) > 10:
                        motion_buffer = motion_buffer[-10:]

                    accuracy = compute_motion_similarity(motion_buffer, motion_reference)
                    last_accuracy = (0.7 * last_accuracy) + (0.3 * accuracy)
                    accuracy_display.metric("🎯 Accuracy", f"{last_accuracy:.2f}%")
                    reps_display.metric("✅ Reps", st.session_state.reps)

                    if accuracy > 80 and not st.session_state.pose_held:
                        st.session_state.reps += 1
                        st.session_state.pose_held = True
                        coach.speak("✅ Great rep!")

                    if accuracy < 40:
                        st.session_state.pose_held = False

                    if accuracy < 60:
                        feedback_placeholder.markdown("### ⚠️ Adjust your form!")
                        coach.speak("Adjust your form!")
                    else:
                        feedback_placeholder.markdown("### ✅ Looking good!")
        else:
            feedback_placeholder.warning("⚠️ No pose detected.")

        cv2.imwrite(temp_file.name, frame)
        if "overlay" in st.session_state:
            try:
                frame=cv2.addweighted(frame, 1.0, st.session_state.overlay, 0.6, 0)
            except Exception:
                pass
        stframe.image(temp_file.name, channels="BGR", use_container_width=True)

        time.sleep(0.5)

    camera.release()
    duration = round(time.time() - st.session_state.start_time, 2)

    log_session(
        pose=pose_name,
        reps=st.session_state.reps,
        feedback_list=list(st.session_state.feedback_collected),
        duration=duration
    )

    st.session_state.running = False
    st.session_state.stop = False
    st.session_state.pose_held = False

    fb = list(st.session_state.feedback_collected)
    stframe.empty()
    feedback_placeholder.empty()
    accuracy_display.empty()
    reps_display.empty()
    stop_button_placeholder.empty()

    summary = f"✅ Session saved! Duration: {duration} sec | Reps: {st.session_state.reps} | Feedbacks: {len(fb)} types."
    st.success(summary)
