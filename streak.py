import streamlit as st
import pandas as pd
from datetime import timedelta
from database.logger import get_all_sessions

st.set_page_config(page_title="🔥 Streak Tracker")
st.title("🔥 Streak Tracker")

data = get_all_sessions()
if not data:
    st.info("Start some sessions to build your streak.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Filter options
    pose_options = df["Pose"].unique().tolist()
    selected_pose = st.selectbox("🧘 Filter by Pose:", ["All"] + pose_options)
    recent_days = st.slider("📅 Show sessions from last X days:", 1, 30, 7)
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=recent_days)

    filtered_df = df.copy()
    if selected_pose != "All":
        filtered_df = filtered_df[filtered_df["Pose"] == selected_pose]
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]

    session_dates = pd.to_datetime(filtered_df["Date"].dt.date).sort_values().unique()
    current_streak = 0
    longest_streak = 0
    today = pd.Timestamp.today().normalize()
    yesterday = today - timedelta(days=1)
    previous_date = None

    for date in reversed(session_dates):
        if previous_date is None:
            if date in [today, yesterday]:
                current_streak = 1
            previous_date = date
        else:
            if (previous_date - date).days == 1:
                current_streak += 1
                previous_date = date
            elif (previous_date - date).days > 1:
                break

    streak = 1
    for i in range(1, len(session_dates)):
        if (session_dates[i] - session_dates[i - 1]).days == 1:
            streak += 1
        else:
            longest_streak = max(longest_streak, streak)
            streak = 1
    longest_streak = max(longest_streak, streak)

    st.metric("🔥 Current Streak (days)", current_streak)
    st.metric("🏅 Longest Streak", longest_streak)
