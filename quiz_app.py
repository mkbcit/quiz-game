import streamlit as st
import pandas as pd
import time

# ---------------------------
# Session state
# ---------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

FILE = "results.csv"

def load_data():
    try:
        return pd.read_csv(FILE)
    except:
        return pd.DataFrame(columns=["Name", "Score", "Time"])

def save_data(df):
    df.to_csv(FILE, index=False)

# ---------------------------
# Title
# ---------------------------
st.title("🧬 Genomics & Metagenomics Challenge for AGC Member")
st.write("Answer all questions. Highest score + fastest time wins! 🏆")

# ---------------------------
# Name input
# ---------------------------
name = st.text_input("Enter your Name / ID")

if st.button("Start Quiz 🚀") and name:
    st.session_state.start_time = time.time()
    st.session_state.submitted = False

# ---------------------------
# Quiz Section
# ---------------------------
if st.session_state.start_time and not st.session_state.submitted:

    st.subheader("Answer all questions:")

    answers = {}

    answers["q1"] = st.radio("1. Which molecule carries genetic information?",
                            ["RNA", "DNA", "Protein", "Lipid"])

    answers["q2"] = st.radio("2. PCR is used to:",
                            ["Sequence DNA", "Amplify DNA", "Cut DNA", "Store DNA"])

    answers["q3"] = st.radio("3. CRISPR-Cas9 is used for:",
                            ["DNA extraction", "Gene editing", "Protein synthesis", "Sequencing"])

    answers["q4"] = st.radio("4. Natural products are produced by:",
                            ["Only synthetic processes", "Living organisms", "Only plants", "Only bacteria"])

    answers["q5"] = st.radio("5. Fermentation is used to:",
                            ["Produce useful products using microbes", "Destroy DNA", "Sequence proteins", "Measure pH"])

    answers["q6"] = st.radio("6. Which RNA carries amino acids?",
                            ["mRNA", "tRNA", "rRNA", "snRNA"])

    answers["q7"] = st.radio("7. Metagenomics studies:",
                            ["Single organisms", "DNA from environmental samples", "Only human DNA", "Protein structures"])

    answers["q8"] = st.radio("8. Which enzyme replicates DNA?",
                            ["RNA polymerase", "DNA polymerase", "Ligase", "Helicase"])

    answers["q9"] = st.radio("9. Microbiome refers to:",
                            ["One bacterium", "All microbes in an environment", "Only pathogens", "Only viruses"])

    answers["q10"] = st.radio("10. Restriction enzymes:",
                             ["Amplify DNA", "Cut DNA at specific sites", "Join DNA", "Translate DNA"])

    answers["q11"] = st.radio("11. ATP is:",
                             ["Genetic material", "Energy currency of cell", "Protein", "Enzyme"])

    answers["q12"] = st.radio("12. Which organelle produces ATP?",
                             ["Nucleus", "Mitochondria", "Ribosome", "Golgi"])

    answers["q13"] = st.radio("13. Point mutation affects:",
                             ["Entire chromosome", "Single nucleotide", "Whole genome", "Proteins only"])

    answers["q14"] = st.radio("14. Bioinformatics is used to:",
                             ["Grow bacteria", "Analyze biological data using computers", "Extract DNA", "Perform PCR"])

    answers["q15"] = st.radio("15. Gut microbiome helps in:",
                             ["Only disease", "Digestion and health", "DNA replication", "Protein synthesis"])

    # ---------------------------
    # Submit Button
    # ---------------------------
    if st.button("Submit Answers"):
        end_time = time.time()
        duration = round(end_time - st.session_state.start_time, 2)

        # Correct answers
        correct = {
            "q1": "DNA",
            "q2": "Amplify DNA",
            "q3": "Gene editing",
            "q4": "Living organisms",
            "q5": "Produce useful products using microbes",
            "q6": "tRNA",
            "q7": "DNA from environmental samples",
            "q8": "DNA polymerase",
            "q9": "All microbes in an environment",
            "q10": "Cut DNA at specific sites",
            "q11": "Energy currency of cell",
            "q12": "Mitochondria",
            "q13": "Single nucleotide",
            "q14": "Analyze biological data using computers",
            "q15": "Digestion and health"
        }

        score = sum([1 for k in correct if answers[k] == correct[k]])

        df = load_data()
        new_entry = pd.DataFrame([[name, score, duration]],
                                 columns=["Name", "Score", "Time"])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)

        st.session_state.submitted = True

        st.success(f"✅ Submitted! Score: {score}/15 | Time: {duration} sec")

# ---------------------------
# Leaderboard (Improved)
# ---------------------------
st.subheader("🏆 Leaderboard")

df = load_data()

if not df.empty:

    # Normalize time (lower is better)
    df["Time_norm"] = df["Time"] / df["Time"].max()

    # Combined performance metric
    df["Performance"] = df["Score"] - df["Time_norm"]

    # Sort: best score first, then fastest time
    df_sorted = df.sort_values(
        by=["Score", "Time"],
        ascending=[False, True]
    ).reset_index(drop=True)

    # Add ranking
    df_sorted["Rank"] = df_sorted.index + 1

    # Medal icons
    def medal(rank):
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        return ""

    df_sorted["🏅"] = df_sorted["Rank"].apply(medal)

    # Final display columns
    df_sorted = df_sorted[["Rank", "🏅", "Name", "Score", "Time"]]

    # Show everything in one page
    st.dataframe(df_sorted, use_container_width=True, height=600)

else:
    st.info("No results yet.")

st.markdown("---")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown(
        "<div style='text-align: center; font-size: 14px;'>"
        "🧬 Biology Quiz Platform <br> Developed by <b>Manosh Biswas, PhD</b> <br> Assistant Professor<br>Computational Biology Lab <br> AGC UM6P "
        "</div>",
        unsafe_allow_html=True
    )

 
