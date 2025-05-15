
import math

# Real reference values for Vriksasana (.npz-derived)
vriksasana_reference = {
    "left_foot_vs_knee": -0.07,
    "right_foot_vs_knee": -0.11,
    "hip_alignment": 0.004,
    "shoulder_alignment": 0.006,
    "back_angle": 87.6,
    "arms_symmetry": 0.004,
    "arms_distance_x": 0.08,
}

# Real reference values for Tadasana (.npz-derived)
tadasana_reference = {
    "feet_distance_x": 0.043,
    "hip_alignment": 0.0013,
    "shoulder_alignment": 0.0061,
    "back_angle": 92.4,
}


def calculate_angle(a, b, c):
    angle = math.degrees(
        math.atan2(c["y"] - b["y"], c["x"] - b["x"]) -
        math.atan2(a["y"] - b["y"], a["x"] - b["x"])
    )
    return abs(angle) if angle >= 0 else abs(angle + 360)


def get_feedback_tags(landmarks):
    tags = []

    left_ankle = landmarks.get("LEFT_ANKLE")
    right_ankle = landmarks.get("RIGHT_ANKLE")
    left_hip = landmarks.get("LEFT_HIP")
    right_hip = landmarks.get("RIGHT_HIP")
    left_shoulder = landmarks.get("LEFT_SHOULDER")
    right_shoulder = landmarks.get("RIGHT_SHOULDER")

    if left_ankle and right_ankle:
        feet_dist = abs(left_ankle["x"] - right_ankle["x"])
        if feet_dist > tadasana_reference["feet_distance_x"] + 0.02:
            tags.append("feet_apart")

    if left_hip and right_hip:
        if abs(left_hip["y"] - right_hip["y"]) > tadasana_reference["hip_alignment"] + 0.02:
            tags.append("hips_unbalanced")

    if left_shoulder and right_shoulder:
        if abs(left_shoulder["y"] - right_shoulder["y"]) > tadasana_reference["shoulder_alignment"] + 0.02:
            tags.append("shoulders_unbalanced")

    if left_hip and left_shoulder and right_shoulder:
        back_angle = calculate_angle(left_hip, left_shoulder, right_shoulder)
        if abs(back_angle - tadasana_reference["back_angle"]) > 10:
            tags.append("back_not_straight")

    if not tags:
        tags.append("pose_correct")

    return tags


def get_feedback_tags_vrikshasana(landmarks):
    tags = []

    left_ankle = landmarks.get("LEFT_ANKLE")
    right_ankle = landmarks.get("RIGHT_ANKLE")
    left_knee = landmarks.get("LEFT_KNEE")
    right_knee = landmarks.get("RIGHT_KNEE")
    left_hip = landmarks.get("LEFT_HIP")
    right_hip = landmarks.get("RIGHT_HIP")
    left_shoulder = landmarks.get("LEFT_SHOULDER")
    right_shoulder = landmarks.get("RIGHT_SHOULDER")
    left_elbow = landmarks.get("LEFT_ELBOW")
    right_elbow = landmarks.get("RIGHT_ELBOW")

    if left_ankle and left_knee:
        delta = left_ankle["y"] - left_knee["y"]
        if delta > vriksasana_reference["left_foot_vs_knee"] + 0.05:
            tags.append("leg_too_low")
        elif delta < vriksasana_reference["left_foot_vs_knee"] - 0.05:
            tags.append("leg_too_high")
    elif right_ankle and right_knee:
        delta = right_ankle["y"] - right_knee["y"]
        if delta > vriksasana_reference["right_foot_vs_knee"] + 0.05:
            tags.append("leg_too_low")
        elif delta < vriksasana_reference["right_foot_vs_knee"] - 0.05:
            tags.append("leg_too_high")

    if left_shoulder and right_shoulder:
        if abs(left_shoulder["y"] - right_shoulder["y"]) > vriksasana_reference["shoulder_alignment"] + 0.02:
            tags.append("shoulders_unbalanced")

    if left_hip and right_hip:
        if abs(left_hip["y"] - right_hip["y"]) > vriksasana_reference["hip_alignment"] + 0.02:
            tags.append("hips_unbalanced")

    if left_elbow and right_elbow:
        symmetry_y = abs(left_elbow["y"] - right_elbow["y"])
        distance_x = abs(left_elbow["x"] - right_elbow["x"])
        if symmetry_y > vriksasana_reference["arms_symmetry"] + 0.02:
            tags.append("arms_not_symmetric")
        if distance_x > vriksasana_reference["arms_distance_x"] + 0.05:
            tags.append("hands_not_joined")

    if left_hip and left_shoulder and right_shoulder:
        back_angle = calculate_angle(left_hip, left_shoulder, right_shoulder)
        if abs(back_angle - vriksasana_reference["back_angle"]) > 10:
            tags.append("back_not_straight")

    if not tags:
        tags.append("pose_correct")

    return tags


feedback_lines = {
    "pose_correct": ["Perfect posture. Hold steady."],
    "back_not_straight": ["Keep your back straight."],
    "shoulders_unbalanced": ["Level your shoulders."],
    "hips_unbalanced": ["Align your hips. Don't tilt sideways."],
    "feet_apart": ["Join your feet together."],
    "leg_too_low": ["Lift your foot higher, place it on the thigh."],
    "leg_too_high": ["Lower your foot slightly to rest it on your thigh."],
    "arms_not_symmetric": ["Raise your arms evenly."],
    "hands_not_joined": ["Join your palms together at your chest."]
}
