import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

CSV_FILE = "workout_log.csv"

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])

# Load data
@st.cache_data
def load_data():
    try:
        return pd.read_csv(CSV_FILE, parse_dates=["Date"])
    except pd.errors.EmptyDataError:
        # Recreate the file with headers if it's empty
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])
        return pd.DataFrame(columns=["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])

data = load_data()

# Main App
st.title("🏋️ Gym Workout Logger")
tabs = st.tabs(["➕ Log Workout", "📂 Workout History", "📈 Progress Charts", "🏆 Personal Bests"])

# Tab 1: Log Workout
with tabs[0]:
    st.subheader("➕ Log a Workout")
    date = st.date_input("Workout Date", value=datetime.today())
    category = st.selectbox("Workout Category", ["Push", "Pull", "Legs", "Full Body", "Other"])
    exercise = st.text_input("Exercise Name")
    num_sets = st.number_input("Number of Sets", min_value=1, max_value=10, step=1)

    with st.form("workout_form"):
        sets_data = []
        for i in range(num_sets):
            st.markdown(f"**Set {i+1}**")
            col1, col2 = st.columns(2)
            reps = col1.number_input(f"Reps (Set {i+1})", min_value=1, step=1, key=f"reps_{i}")
            weight = col2.number_input(f"Weight (kg) (Set {i+1})", min_value=0.0, step=0.5, key=f"weight_{i}")
            sets_data.append((reps, weight))

        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Log Workout")

    if submitted:
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            for idx, (reps, weight) in enumerate(sets_data):
                writer.writerow([date, category, exercise, idx + 1, reps, weight, notes if idx == 0 else ""])
        st.success("Workout saved!")
        st.rerun()  # Refresh the page after saving

# Tab 2: Workout History
with tabs[1]:
    st.subheader("📂 Your Logged Workouts")
    if data.empty:
        st.info("No data found.")
    else:
        st.dataframe(data.sort_values("Date", ascending=False))

    # Clear Data Button
    if st.button("Clear All Workout Data"):
        os.remove(CSV_FILE)  # Delete the CSV file
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Exercise", "Set Number", "Reps", "Weight (kg)", "Notes"])  # Reset headers
        st.success("All workout data has been cleared!")
        st.rerun()  # Reload the app

# Tab 4: Personal Bests
with tabs[2]:
    st.subheader("🏆 Personal Bests")
    if data.empty:
        st.info("No data available.")
    else:
        bests = data.groupby("Exercise")["Weight (kg)"].max().reset_index()
        bests.columns = ["Exercise", "Max Weight (kg)"]
        st.table(bests)
