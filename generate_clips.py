# backend/voice/generate_clips.py

from gtts import gTTS
import os

feedback_lines = {
    "pose_correct": "Perfect posture. Hold steady.",
    "back_not_straight": "Keep your back straight.",
    "shoulders_unbalanced": "Level your shoulders.",
    "hips_unbalanced": "Align your hips. Don't tilt sideways.",
    "feet_apart": "Join your feet together.",
    "leg_too_low": "Lift your foot higher, place it on the thigh.",
    "leg_too_high": "Lower your foot slightly to rest it on your thigh.",
    "arms_not_symmetric": "Raise your arms evenly.",
    "hands_not_joined": "Join your palms together at your chest.",
    "pose_not_visible": "Your posture is not fully visible. Please adjust your position.",
    "minor_correction": "Minor adjustments needed.",
    "major_correction": "Major correction needed.",
    "adjust_form": "Adjust your form!",
    "great_rep": "Great rep!",
    "start_session": "Session started. Your form will now be monitored.",
}

output_dir = os.path.join("voice_feedback_clips")
os.makedirs(output_dir, exist_ok=True)

for tag, text in feedback_lines.items():
    path = os.path.join(output_dir, f"{tag}.mp3")
    if not os.path.exists(path):
        tts = gTTS(text=text, lang='en')
        tts.save(path)
        print(f"✅ Saved: {tag}.mp3")
    else:
        print(f"✔ Already exists: {tag}.mp3")
