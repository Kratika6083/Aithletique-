import streamlit as st
import pandas as pd
from datetime import timedelta
import calplot
import matplotlib.pyplot as plt
from database.logger import get_all_sessions

st.set_page_config(page_title="📅 Calendar")
st.title("📅 Calendar View")

data = get_all_sessions()
if not data:
    st.info("No data available to display calendar.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Filters
    pose_options = df["Pose"].unique().tolist()
    selected_pose = st.selectbox("🧘 Filter by Pose:", ["All"] + pose_options)
    recent_days = st.slider("📅 Show sessions from last X days:", 1, 30, 7)
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=recent_days)

    filtered_df = df.copy()
    if selected_pose != "All":
        filtered_df = filtered_df[filtered_df["Pose"] == selected_pose]
    filtered_df = filtered_df[filtered_df["Date"] >= cutoff]

    if filtered_df.empty:
        st.warning("No calendar data available for selected filters.")
    else:
        filtered_df["date"] = pd.to_datetime(filtered_df["Date"].dt.date)
        session_counts = filtered_df.groupby("date").size()
        session_counts.index = pd.to_datetime(session_counts.index)
        fig, ax = calplot.calplot(session_counts, cmap='YlGn', colorbar=True, suptitle='Your Activity Calendar')
        st.pyplot(fig)
