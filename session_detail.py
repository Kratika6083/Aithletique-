import streamlit as st
import pandas as pd
from datetime import timedelta
from database.logger import get_all_sessions

st.set_page_config(page_title="📌 Session Details")
st.title("📌 Session Details")

data = get_all_sessions()
if not data:
    st.info("No session records available.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date", ascending=False)

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
        st.warning("No sessions found for the selected filters.")
    else:
        for index, row in filtered_df.iterrows():
            with st.expander(f"📅 {row['Date'].strftime('%b %d, %Y')} – {row['Pose'].title()}"):
                st.markdown(f"**Reps:** {row['Reps']}")
                st.markdown(f"**Duration:** {round(row['Duration (sec)'], 1)} sec")
                st.markdown("**Feedback:**")
                st.code(row['Feedback'])
