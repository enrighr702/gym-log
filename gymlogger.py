import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

EXERCISE_OPTIONS = {
    "Push": ["Bench Press", "Viking Press", "Incline Dumbbell Press", "Triceps Pushdown", "Dips", "Machine Incline Chest Press", "Machine Chest Press"],
    "Pull": ["Pull-Ups", "T-Bar Row", "Face Pull", "Bicep Preacher Curl", "Incline Dumbbell Curl", "Seated Row", "Lat Pulldown", "Chin-Ups"],
    "Legs": ["Squat", "Lunges", "Leg Press", "Calf Raises", "Back Extensions", "RDL"],
    "Shoulder + Arms": ["Viking Press", "Dumbbell Shoulder Press", "Lateral Raises", "Face Pulls", "Cable Bicep Curl", "Tricep Extension", "Dumbbell Curls"],
    "Other": []
}

CSV_FILE = "workout_log.csv"

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])

# --- Streamlit App ---
st.set_page_config(page_title="Gym Logger", layout="centered")
st.title("🏋️ Gym Workout Logger")

# Handle form reset
if st.query_params.get("reset") == "true":
    st.query_params.update(reset=None)

# Tabs
tabs = st.tabs(["➕ Log Workout", "📂 Workout History", "📈 Progress Charts", "🏆 Personal Bests"])

# Tab 1: Log Workout
with tabs[0]:
    st.subheader("➕ Log a Workout")
    date = st.date_input("Workout Date", value=datetime.today(), key="date")
    category = st.selectbox("Workout Category", ["Push", "Pull", "Legs", "Shoulder + Arms", "Other"], key="category")
    exercise_options = EXERCISE_OPTIONS.get(category, [])
    
    if exercise_options:
        exercise = st.selectbox("Exercise", exercise_options + ["Other"], key="exercise_select")
        if exercise == "Other":
            exercise = st.text_input("Enter custom exercise name", key="custom_exercise")
    else:
        exercise = st.text_input("Exercise Name", key="exercise_name")
    num_sets = st.number_input("Number of Sets", min_value=1, max_value=10, step=1, key="num_sets")

    with st.form("workout_form"):
        sets_data = []
        for i in range(int(num_sets)):
            st.markdown(f"**Set {i + 1}**")
            col1, col2 = st.columns(2)
            reps = col1.number_input(f"Reps (Set {i + 1})", min_value=1, step=1, key=f"reps_{i}")
            weight = col2.number_input(f"Weight (kg) (Set {i + 1})", min_value=0.0, step=0.5, key=f"weight_{i}")
            sets_data.append((reps, weight))

        notes = st.text_area("Notes (optional)", key="notes")
        submitted = st.form_submit_button("Log Workout")

    if submitted:
        try:
            with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                for idx, (reps, weight) in enumerate(sets_data):
                    writer.writerow([
                        date, category, exercise,
                        idx + 1, reps, weight,
                        notes if idx == 0 else ""
                    ])
                file.flush()
                os.fsync(file.fileno())
            st.success("✅ Workout saved!")
    
            # ✅ Update query param to reset form
            st.query_params.update(reset="true")
            st.rerun()
    
        except Exception as e:
            st.error(f"❌ Error saving workout: {e}")

# Tab 2: Workout History
with tabs[1]:
    st.subheader("📂 Your Logged Workouts")
    try:
        data = pd.read_csv(CSV_FILE, parse_dates=["Date"])
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])

    if data.empty:
        st.info("No data found.")
    else:
        st.dataframe(data.sort_values("Date", ascending=False))

    if st.button("🧹 Clear All Workout Data"):
        os.remove(CSV_FILE)
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])
        st.success("All workout data has been cleared!")
        st.rerun()

# Tab 3: Progress Charts
with tabs[2]:
    st.subheader("📈 Progress Charts")
    data = pd.read_csv(CSV_FILE, parse_dates=["Date"])
    if data.empty:
        st.info("No data to show.")
    else:
        exercise_list = data["Exercise"].unique().tolist()
        selected_exercise = st.selectbox("Select Exercise", exercise_list)

        chart_data = data[data["Exercise"] == selected_exercise]
        chart_data = chart_data.groupby("Date")["Weight (kg)"].max().reset_index()

        st.line_chart(chart_data.set_index("Date"))

# Tab 4: Personal Bests
with tabs[3]:
    st.subheader("🏆 Personal Bests")
    data = pd.read_csv(CSV_FILE, parse_dates=["Date"])
    if data.empty:
        st.info("No data available.")
    else:
        bests = data.groupby("Exercise")["Weight (kg)"].max().reset_index()
        bests.columns = ["Exercise", "Max Weight (kg)"]
        st.table(bests)
