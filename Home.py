import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'components')))
from webcam_feed import run_pose_detection

import streamlit as st
import os
import random
import glob
from components.webcam_feed import run_pose_detection
from meditation.meditation_features import run_meditation_session
from components.workout_main import start_squat_workout
from components.multi_workout_main import (
    start_pushup_workout,
    start_plank_workout,
    start_pullup_workout
)
st.set_page_config(page_title="Aithletique", layout="centered")

st.markdown("""
<style>
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #f6336610;
    color: #f63366;
    font-weight: 600;
}
.stButton>button {
    background-color: #F63366;
    color: white;
    border-radius: 8px;
    font-size: 1.1em;
    padding: 0.5em 1em;
}
</style>
""", unsafe_allow_html=True)
# Sidebar branding
with st.sidebar:
    st.image("assets\logo2.png", width=120)
    st.markdown("### 🧘 Aithletique Coach")
    st.caption("Train Smarter. Perform Better.")

# Existing Home.py logic continues below...
# (Insert your main homepage logic under this block)

# -------------------- Page Setup -------------------- #

# -------------------- Branding Header -------------------- #

st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='font-size: 3em; color: #F63366;'>Aithletique</h1>
        <p style='font-size: 1.3em; color: #AAAAAA;'>Your AI-Powered Real-Time Posture Coach</p>
    </div>
""", unsafe_allow_html=True)

# -------------------- Inspirational Quote -------------------- #
quotes = [
    "Push harder than yesterday if you want a different tomorrow.",
    "Your body can stand almost anything. It’s your mind you have to convince.",
    "Train insane or remain the same.","Yoga is the journey of the self, through the self, to the self.",
      "Inhale the future, exhale the past.",
        "Meditation is not evasion; it is a serene encounter with reality.", 
        "The pose begins when you want to leave it.",
          "Silence isn’t empty, it’s full of answers.",
                "Your body can stand almost anything. It’s your mind you have to convince.", 
            "The only bad workout is the one that didn’t happen.", "Sweat is just fat crying.", 
 "Push yourself because no one else is going to do it for you.",
 "Discipline is doing what needs to be done, even when you don’t want to do it.",
   "Don’t limit your challenges. Challenge your limits.",
 "Fall in love with taking care of yourself.",
    "The difference between try and triumph is a little 'umph'.",
        "Success doesn’t come from what you do occasionally, it comes from what you do consistently.",
         "Train like a beast, look like a beauty."

]
st.info(random.choice(quotes))

# -------------------- Meditation State -------------------- #
if "meditation_started" not in st.session_state:
    st.session_state["meditation_started"] = False

if st.session_state.get("show_summary"):
    st.session_state["__tabs_Yoga & Meditation"] = 0

# -------------------- Tabs Layout -------------------- #
tabs = st.tabs(["🧘 Yoga & Meditation", "🏋 Workout & Training"])

# -------------------- Yoga & Meditation Tab -------------------- #
with tabs[0]:
    pose_folder = "pose_references"
    npz_files = [f for f in os.listdir(pose_folder) if f.endswith(".npz")]
    yoga_poses = [os.path.splitext(f)[0].replace("_", " ").title() for f in npz_files]
    yoga_poses.append("Meditation")

    pose_type = st.selectbox("🎯 Choose Your Activity:", sorted(yoga_poses), key="yoga_select")
    st.markdown(f"📝 Live feedback for: *{pose_type}*")

    # 💡 How to Use Aithletique
    with st.expander("💡 How to Use Aithletique?"):
        st.markdown("""
        1. Choose an activity from the dropdown menu above.
        2. Click "Start" to begin your session.
        3. Follow on-screen and audio feedback for posture correction.
        4. Use the Progress tab to track your improvement.
        """)

    # 🖼️ Dynamic Pose Reference Image
    dataset_path = "D:/Aithletique/dataset"
    pose_key = pose_type.lower().replace(" ", "_")
    pose_dir = os.path.join(dataset_path, pose_key)
    if os.path.exists(pose_dir):
        image_files = glob.glob(os.path.join(pose_dir, "*.jpg")) + glob.glob(os.path.join(pose_dir, "*.png"))
        if image_files:
            chosen_image = random.choice(image_files)
            st.image(chosen_image, caption=f"Reference: {pose_type}")

    # Meditation Block
    if pose_type.lower() == "meditation":
        duration = st.slider("⏳ Meditation Duration (minutes)", 1, 30, 5, key="med_dur")

        if st.button("🧘 Start Meditation", key="start_meditation_btn"):
            st.session_state["show_summary"] = False
            st.session_state["meditation_started"] = True
            st.session_state["summary_data"] = {}
            st.rerun()

        if st.session_state.get("meditation_started", False) and st.session_state.get("meditation_running", True):
            run_meditation_session(duration_minutes=duration)

    # Yoga Pose Block
    else:
        st.markdown("""
            <style>
            .stButton>button {
                background-color: #F63366;
                color: white;
                border-radius: 8px;
                font-size: 1.1em;
                padding: 0.5em 1em;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("🎥 Start Yoga Session", key="start_yoga"):
            run_pose_detection(pose_name=pose_type.lower(), category="Yoga & Meditation")

# -------------------- Workout Tab -------------------- #
with tabs[1]:
    pose_type = st.selectbox("🎯 Choose Your Activity:", ["Squat", "Pushup", "Plank", "Pull-up"], key="workout_select")
    st.markdown(f"📝 Live feedback for: *{pose_type}*")

    # 🎞️ Show workout reference video dynamically
    video_folder = "D:/Aithletique/workout_videos"
    video_files = glob.glob(os.path.join(video_folder, f"*{pose_type.lower()}*.mp4"))
    if video_files:
        video_to_play = video_files[0]
        st.video(video_to_play, start_time=0)
        st.caption("Showing preview clip. Full session starts when you click the button.")

    if st.button("🎥 Start Workout Session"):
        if pose_type.lower() == "squat":
            start_squat_workout()
        elif pose_type.lower() == "pushup":
            start_pushup_workout()
        elif pose_type.lower() == "plank":
            start_plank_workout()
        elif pose_type.lower() == "pull-up":
            start_pullup_workout()
        else:
            run_pose_detection(pose_name=pose_type.lower(), category="Workout & Training")

# -------------------- Feedback Form -------------------- #
st.markdown("---")
with st.form("feedback_form"):
    st.subheader("📬 Send Us Feedback")
    name = st.text_input("Your Name")
    user_email = st.text_input("Your Email")
    feedback_msg = st.text_area("Your Feedback")
    submitted = st.form_submit_button("Send 🚀")

    if submitted:
        if name and user_email and feedback_msg:
            import smtplib
            from email.mime.text import MIMEText

            sender_email = "kbhadauria4005@gmail.com"  # your email
            app_password = "pwlrdmlxgqpawdfi"  # app password from Gmail
            recipient_email = "kratikabhadauria6083@gmail.com"  # where you want to receive feedback

            subject = "📬 New Feedback from Aithletique"
            body = f"""
            Name: {name}
            Email: {user_email}

            Feedback:
            {feedback_msg}
            """

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient_email

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, recipient_email, msg.as_string())
                st.success("✅ Thanks! Your feedback has been sent.")
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
        else:
            st.warning("⚠️ Please fill in all fields.")


# -------------------- User Stats (Optional Dashboard) -------------------- #
# with st.expander("📊 Show User Stats"):
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Sessions", "128", "+4 Today")
#     col2.metric("Avg. Accuracy", "91%", "↑ 3%")
#     col3.metric("Users Active", "12", "Live")
