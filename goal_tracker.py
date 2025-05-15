import streamlit as st
import pandas as pd
import time
from datetime import timedelta
from database.logger import get_all_sessions

st.set_page_config(page_title="🎯 Goal Tracker")

st.markdown("""
<div style='text-align: center;'>
    <h1 style='color:#F63366;'>🎯 Weekly Goal Progress</h1>
    <p style='color:#666;'>Track your consistency and aim for better!</p>
</div>
""", unsafe_allow_html=True)

data = get_all_sessions()

if not data:
    st.info("No sessions yet. Complete some to start tracking goals.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Filters
    with st.container():
        st.markdown("### 🔍 Filter Options")
        pose_options = df["Pose"].unique().tolist()
        selected_pose = st.selectbox("🧘 Filter by Pose:", ["All"] + pose_options)
        recent_days = st.slider("📅 Show sessions from last X days:", 1, 30, 7)
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=recent_days)

    filtered_df = df.copy()
    if selected_pose != "All":
        filtered_df = filtered_df[filtered_df["Pose"] == selected_pose]
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]

    if filtered_df.empty:
        st.warning("No goal data available for selected filters.")
    else:
        with st.container():
            weekly_goal = st.slider("🎯 Set your weekly session goal:", 1, 14, 5)
            weekly_sessions = len(filtered_df)
            goal_percent = int((weekly_sessions / weekly_goal) * 100)
            goal_percent = min(goal_percent, 100)

            st.markdown("### 📊 Goal Completion")
            with st.spinner("Calculating your progress..."):
                st.progress(goal_percent)
                time.sleep(0.5)
                if weekly_sessions >= weekly_goal:
                    st.success("🏆 Goal achieved! Great work!")
                    st.balloons()
                elif weekly_sessions == 0:
                    st.warning("🚀 Let's get moving! Start a session today.")
                else:
                    st.info("⏳ Keep going – you're getting closer!")

            st.write(f"✅ You've completed **{weekly_sessions}/{weekly_goal}** sessions this week!")
