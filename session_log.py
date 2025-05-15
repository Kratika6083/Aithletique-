import streamlit as st
import pandas as pd
from database.logger import get_all_sessions

st.set_page_config(page_title="📋 Session Log")
st.title("📋 Session Log")

data = get_all_sessions()
if not data:
    st.info("No session logs found.")
else:
    df = pd.DataFrame(data, columns=["ID", "Pose", "Reps", "Feedback", "Duration (sec)", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date", ascending=False)

    def summarize_feedback(raw_text):
        if not raw_text or pd.isna(raw_text):
            return "❔ No feedback available."
        parts = [p.strip() for p in raw_text.split(";") if p.strip()]
        good = [p for p in parts if "✅" in p or "Good posture" in p or "Soft breathing" in p]
        issues = [p for p in parts if "❌" in p or "Not breathing" in p or "Go deeper" in p or "Keep your head" in p]
        tips = [p for p in parts if "Try" in p or "Hold" in p or "Slow" in p]
        summary = ""
        if good:
            summary += f"✅ Good: {', '.join(good[:2])}. "
        if issues:
            summary += f"⚠️ Needs work: {', '.join(issues[:2])}. "
        if tips:
            summary += f"🔁 Tip: {', '.join(tips[:1])}."
        return summary or "😐 Neutral session."

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
        st.warning("No logs match the selected filters.")
    else:
        filtered_df["Feedback Summary"] = filtered_df["Feedback"].apply(summarize_feedback)
        st.dataframe(filtered_df[["Date", "Pose", "Reps", "Feedback Summary"]], use_container_width=True)
