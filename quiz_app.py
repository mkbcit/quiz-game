import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ---------------------------
# Initialize session state
# ---------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ---------------------------
# Load leaderboard file
# ---------------------------
FILE = "results.csv"

def load_data():
    try:
        return pd.read_csv(FILE)
    except:
        return pd.DataFrame(columns=["Name", "Score", "Time"])

def save_data(df):
    df.to_csv(FILE, index=False)

# ---------------------------
# UI Title
# ---------------------------
st.title("🧬 Microbiology Quiz Challenge")
st.write("Answer all questions as fast as possible. Top score + fastest time wins! 🏆")

# ---------------------------
# Name Input
# ---------------------------
name = st.text_input("Enter your Name / ID")

if st.button("Start Quiz 🚀") and name:
    st.session_state.start_time = time.time()
    st.session_state.submitted = False

# ---------------------------
# Quiz Section
# ---------------------------
if st.session_state.start_time and not st.session_state.submitted:

    st.subheader("Answer the questions:")

    q1 = st.radio("1. DNA carries genetic information?", ["RNA", "DNA", "Protein"])
    q2 = st.radio("2. PCR is used to:", ["Amplify DNA", "Cut DNA", "Store DNA"])
    q3 = st.radio("3. CRISPR is used for:", ["Gene editing", "Sequencing", "Extraction"])
    q4 = st.radio("4. Microbiome means:", ["Single microbe", "All microbes", "Only pathogens"])
    q5 = st.radio("5. ATP is:", ["Energy molecule", "Protein", "DNA"])
    
    if st.button("Submit Answers"):
        end_time = time.time()
        duration = round(end_time - st.session_state.start_time, 2)

        score = 0
        if q1 == "DNA": score += 1
        if q2 == "Amplify DNA": score += 1
        if q3 == "Gene editing": score += 1
        if q4 == "All microbes": score += 1
        if q5 == "Energy molecule": score += 1

        # Save result
        df = load_data()
        new_entry = pd.DataFrame([[name, score, duration]],
                                 columns=["Name", "Score", "Time"])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)

        st.session_state.submitted = True

        st.success(f"✅ Submitted! Score: {score}/5 | Time: {duration} sec")

# ---------------------------
# Leaderboard
# ---------------------------
st.subheader("🏆 Leaderboard")

df = load_data()

if not df.empty:
    df_sorted = df.sort_values(by=["Score", "Time"], ascending=[False, True])
    st.dataframe(df_sorted.head(10))
else:
    st.write("No results yet.")