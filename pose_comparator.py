import numpy as np
import math

IMPORTANT_ANGLE_PAIRS = [
    (23, 25, 27),  # Right Hip-Knee-Ankle
    (24, 26, 28),  # Left Hip-Knee-Ankle
    (11, 13, 15),  # Right Shoulder-Elbow-Wrist
    (12, 14, 16),  # Left Shoulder-Elbow-Wrist
    (11, 23, 25),  # Right Shoulder-Hip-Knee
    (12, 24, 26),  # Left Shoulder-Hip-Knee
    (23, 11, 13),  # Hip-Shoulder-Elbow Right
    (24, 12, 14)   # Hip-Shoulder-Elbow Left
]

EXCLUDED_JOINTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Mostly face joints

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ab = a - b
    cb = c - b
    cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def extract_important_angles_safe(landmarks_list):
    angles = []
    for (a, b, c) in IMPORTANT_ANGLE_PAIRS:
        if a < len(landmarks_list) and b < len(landmarks_list) and c < len(landmarks_list):
            a_point = landmarks_list[a][:3]
            b_point = landmarks_list[b][:3]
            c_point = landmarks_list[c][:3]
            angle = calculate_angle(a_point, b_point, c_point)
            angles.append(angle)
        else:
            angles.append(0)
    return np.array(angles)

def load_single_reference_landmarks(filepath):
    data = np.load(filepath)
    return data['landmarks']

def flip_left_right_angles(angles_array):
    flip_indices = [1, 0, 3, 2, 5, 4, 7, 6]
    flipped = angles_array.copy()
    for i, j in enumerate(flip_indices):
        flipped[i] = angles_array[j]
    return flipped

def compute_pose_accuracy(live_landmarks, reference_landmarks_list):
    live_angles = extract_important_angles_safe(live_landmarks)
    live_flipped = flip_left_right_angles(live_angles)
    best_score = 0
    for ref_landmarks in reference_landmarks_list:
        ref_angles = extract_important_angles_safe(ref_landmarks)
        if live_angles.shape != ref_angles.shape:
            continue
        diff_normal = np.abs(live_angles - ref_angles)
        accuracy_normal = max(0, 100 - np.mean(diff_normal))
        diff_flipped = np.abs(live_flipped - ref_angles)
        accuracy_flipped = max(0, 100 - np.mean(diff_flipped))
        accuracy = max(accuracy_normal, accuracy_flipped)
        if accuracy > best_score:
            best_score = accuracy
    return best_score

def check_enough_landmarks(landmarks_list, required_ids=[11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 31, 32]):
    visible_count = 0
    for idx in required_ids:
        if idx < len(landmarks_list):
            visibility = landmarks_list[idx][3]
            if visibility >= 0.05:
                visible_count += 1
    return visible_count >= int(0.75 * len(required_ids))

def generate_directional_feedback(user_landmarks, ref_landmarks, joint_names, threshold=0.01):
    import random
    feedback = []
    templates = [
        "Move your {joint} slightly {dir}.",
        "Adjust your {joint} a bit {dir}.",
        "Shift your {joint} slightly {dir}.",
        "Try moving your {joint} slightly {dir}.",
        "Lift your {joint} a little {dir}."
    ]
    for i, (user, ref) in enumerate(zip(user_landmarks, ref_landmarks)):
        if i in EXCLUDED_JOINTS:
            continue
        try:
            ux, uy = float(user[0]), float(user[1])
            rx, ry = float(ref[0]), float(ref[1])
        except Exception:
            continue
        dx = ux - rx
        dy = uy - ry
        directions = []
        if abs(dy) > threshold:
            directions.append("up" if dy < 0 else "down")
        if abs(dx) > threshold:
            directions.append("right" if dx > 0 else "left")
        if directions:
            joint = joint_names.get(i, f"joint {i}")
            for d in directions:
                sentence = random.choice(templates).format(joint=joint, dir=d)
                feedback.append(sentence)
    return feedback

def generate_advanced_feedback(user_landmarks, ref_landmarks, joint_names, angle_threshold=20):
    feedback = []
    user_angles = extract_important_angles_safe(user_landmarks)
    ref_angles = extract_important_angles_safe(ref_landmarks)
    angle_diffs = user_angles - ref_angles
    joint_angle_descriptions = [
        ("right knee", "Bend your right knee a little more."),
        ("left knee", "Bend your left knee a little more."),
        ("right hip", "Open your right hip slightly."),
        ("left hip", "Open your left hip slightly."),
        ("right elbow", "Try straightening your right arm a bit."),
        ("left elbow", "Try straightening your left arm a bit."),
        ("right shoulder", "Relax your right shoulder and keep it aligned."),
        ("left shoulder", "Relax your left shoulder and keep it aligned.")
    ]
    for i, diff in enumerate(angle_diffs):
        if abs(diff) > angle_threshold:
            feedback.append(joint_angle_descriptions[i][1])
    return feedback

def generate_balance_feedback(user_landmarks, threshold=0.05):
    try:
        left_shoulder = np.array(user_landmarks[11][:2])
        right_shoulder = np.array(user_landmarks[12][:2])
        midline = (left_shoulder + right_shoulder) / 2

        left_hip = np.array(user_landmarks[23][:2])
        right_hip = np.array(user_landmarks[24][:2])
        base = (left_hip + right_hip) / 2

        dx = midline[0] - base[0]
        dy = midline[1] - base[1]

        if abs(dx) > threshold:
            return ["Your body is leaning slightly. Try to stay centered."]
        if dy < -threshold:
            return ["You are tilting backward. Shift your weight forward."]
        if dy > threshold:
            return ["You are leaning too far forward. Pull your upper body back a bit."]
    except:
        pass
    return []
