import streamlit as st
import pandas as pd
from database.logger import get_all_sessions
from datetime import timedelta

st.set_page_config(page_title="📈 Session Summary")

st.markdown("""
<div style="text-align:center;">
    <h1 style="color:#F63366;">📈 My Session Summary</h1>
</div>
""", unsafe_allow_html=True)

data = get_all_sessions()
if not data:
    st.info("No session data available yet.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])

    # Filters
    pose_options = df["Pose"].unique().tolist()
    selected_pose = st.selectbox("🧘 Filter by Pose:", ["All"] + pose_options)
    days = st.slider("📅 Days to show", 1, 30, 7)
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)

    filtered = df.copy()
    if selected_pose != "All":
        filtered = filtered[filtered["Pose"] == selected_pose]
    filtered = filtered[filtered["Date"] >= cutoff]

    if filtered.empty:
        st.warning("No data for selected filters.")
    else:
        total_sessions = len(filtered)
        total_duration = filtered["Duration (sec)"].sum()
        common_pose = filtered["Pose"].mode()[0]

        with st.container():
            st.markdown("### 🔢 Key Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sessions", total_sessions)
            with col2:
                st.metric("Total Time (min)", round(total_duration/60, 1))
            with col3:
                st.metric("Top Pose", common_pose)

        with st.container():
            st.markdown("### 📥 Download Your Report")
            csv = filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📁 Export CSV", csv, "aithletique_summary.csv", mime="text/csv")
