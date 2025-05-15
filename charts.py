import streamlit as st
import pandas as pd
import altair as alt
from database.logger import get_all_sessions

st.set_page_config(page_title="📊 Charts")
st.title("📊 Visual Progress")

data = get_all_sessions()
if not data:
    st.info("No data available to visualize.")
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
        st.warning("No data available for the selected filters.")
    else:
        chart_metric = st.radio("📈 Chart Metric:", ["Reps", "Duration"], horizontal=True)
        if len(filtered_df) >= 2:
            chart_data = filtered_df[["Date", "Pose", "Reps", "Duration (sec)"]].copy().sort_values("Date")
            y_field = "Reps" if chart_metric == "Reps" else "Duration (sec)"
            line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x=alt.X("Date:T", title="Session Date"),
                y=alt.Y(f"{y_field}:Q", title=chart_metric),
                color="Pose:N",
                tooltip=["Date", "Pose", y_field]
            ).properties(height=300)
            st.altair_chart(line_chart, use_container_width=True)

            pose_counts = filtered_df["Pose"].value_counts().reset_index()
            pose_counts.columns = ["Pose", "Sessions"]
            st.markdown("### 🏋️ Session Count by Pose")
            bar_chart = alt.Chart(pose_counts).mark_bar().encode(
                x=alt.X("Pose:N"),
                y=alt.Y("Sessions:Q"),
                color="Pose:N"
            ).properties(height=250)
            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("📉 Not enough data to plot charts.")
