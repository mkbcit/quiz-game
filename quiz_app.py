import streamlit as st
import pandas as pd
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================================================================
# 👤 DEVELOPER / AUTHOR IDENTIFICATION & AFFILIATION
# =============================================================================
AUTHOR_NAME = "Manosh Biswas, PhD"                # e.g., "Manosh Biswas, PhD"
AUTHOR_TITLE = "Assistant Professor Computational Biology "    # e.g., "Assistant Professor"
AUTHOR_AFFILIATION = " AGC UM6P"  # e.g., "  Assistant Professor Computational Biology AGC UM6P sity"

# ---------------------------
# Email Credentials & Configuration
# ---------------------------
# Replace these credentials with your actual SMTP details or use st.secrets
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use an App Password (for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

FILE = "results.csv"

# ---------------------------
# CSV Helper Functions
# ---------------------------
def load_data():
    try:
        return pd.read_csv(FILE)
    except Exception:
        return pd.DataFrame(columns=["Name", "Email", "Score", "Time"])

def save_data(df):
    df.to_csv(FILE, index=False)

# ---------------------------
# Quiz Dataset & Answer Key
# ---------------------------
QUIZ_DATA = [
    {
        "id": "q1",
        "question": "1. Which organelle is known as the site of photosynthesis in plant cells?",
        "options": ["Mitochondria", "Chloroplast", "Golgi Body", "Endoplasmic Reticulum"],
        "correct": "Chloroplast"
    },
    {
        "id": "q2",
        "question": "2. Which vascular tissue is responsible for transporting water and minerals?",
        "options": ["Phloem", "Xylem", "Cortex", "Pith"],
        "correct": "Xylem"
    },
    {
        "id": "q3",
        "question": "3. What is the primary component of plant cell walls?",
        "options": ["Chitin", "Peptidoglycan", "Cellulose", "Keratin"],
        "correct": "Cellulose"
    },
    {
        "id": "q4",
        "question": "4. Which plant hormone is primarily responsible for stem elongation?",
        "options": ["Auxin", "Abscisic Acid", "Ethylene", "Cytokinin"],
        "correct": "Auxin"
    },
    {
        "id": "q5",
        "question": "5. Double fertilization is a characteristic feature of which group?",
        "options": ["Bryophytes", "Pteridophytes", "Gymnosperms", "Angiosperms"],
        "correct": "Angiosperms"
    },
    {
        "id": "q6",
        "question": "6. Which light spectrum is most effective for photosynthesis?",
        "options": ["Green and Yellow", "Blue and Red", "UV and Infrared", "Orange and Green"],
        "correct": "Blue and Red"
    },
    {
        "id": "q7",
        "question": "7. Stomata opening and closing is directly controlled by:",
        "options": ["Epidermal cells", "Guard cells", "Companion cells", "Mesophyll cells"],
        "correct": "Guard cells"
    },
    {
        "id": "q8",
        "question": "8. Which gas is released as a byproduct during the light reactions?",
        "options": ["Carbon Dioxide", "Oxygen", "Nitrogen", "Methane"],
        "correct": "Oxygen"
    },
    {
        "id": "q9",
        "question": "9. Pteridophytes are commonly known as:",
        "options": ["Flowering plants", "Vascular cryptogams", "Non-vascular plants", "Naked seed plants"],
        "correct": "Vascular cryptogams"
    },
    {
        "id": "q10",
        "question": "10. The study of fungi is known as:",
        "options": ["Phycology", "Mycology", "Bryology", "Paleobotany"],
        "correct": "Mycology"
    },
    {
        "id": "q11",
        "question": "11. In DNA structure, Adenine pairs with:",
        "options": ["Guanine", "Cytosine", "Thymine", "Uracil"],
        "correct": "Thymine"
    },
    {
        "id": "q12",
        "question": "12. Which type of RNA carries amino acids during protein synthesis?",
        "options": ["mRNA", "tRNA", "rRNA", "snRNA"],
        "correct": "tRNA"
    },
    {
        "id": "q13",
        "question": "13. Naked seeds (unenclosed inside a fruit) are characteristic of:",
        "options": ["Bryophytes", "Angiosperms", "Gymnosperms", "Algae"],
        "correct": "Gymnosperms"
    },
    {
        "id": "q14",
        "question": "14. Which enzyme is responsible for fixing carbon dioxide in C3 plants?",
        "options": ["PEP carboxylase", "RuBisCO", "ATP synthase", "DNA polymerase"],
        "correct": "RuBisCO"
    },
    {
        "id": "q15",
        "question": "15. A symbiotic relationship between algae and fungi is called a:",
        "options": ["Mycorrhiza", "Lichen", "Rhizobium", "Moss"],
        "correct": "Lichen"
    },
    {
        "id": "q16",
        "question": "16. Water loss in the form of vapor through stomata is termed:",
        "options": ["Guttation", "Transpiration", "Osmosis", "Imbibition"],
        "correct": "Transpiration"
    },
    {
        "id": "q17",
        "question": "17. Which molecule serves as the main cellular energy currency?",
        "options": ["NADPH", "Glucose", "ATP", "Pyruvate"],
        "correct": "ATP"
    },
    {
        "id": "q18",
        "question": "18. In which year was the University of Rajshahi established?",
        "options": ["1921", "1952", "1953", "1971"],
        "correct": "1953"
    },
    {
        "id": "q19",
        "question": "19. Who was the founding Vice-Chancellor of Rajshahi University?",
        "options": ["Dr. Itrat Husain Zuberi", "Dr. Shamsuzzoha", "Prof. Mazharul Islam", "Dr. Muhammad Shahidullah"],
        "correct": "Dr. Itrat Husain Zuberi"
    },
    {
        "id": "q20",
        "question": "20. Which monument in RU commemorates the 1969 Uprising and 1971 Liberation War?",
        "options": ["Shabash Bangladesh", "Aparajeyo Bangla", "National Martyrs' Monument", "Central Shaheed Minar"],
        "correct": "Shabash Bangladesh"
    }
]

# ---------------------------
# Email Sender Function
# ---------------------------
def send_feedback_email(recipient_email, user_name, score, duration, user_answers):
    """Sends an HTML formatted email feedback containing full question breakdown."""
    subject = "Your RU Botany Challenge Results and Answer Key 🌿"

    feedback_rows = ""
    for item in QUIZ_DATA:
        q_text = item["question"]
        user_ans = user_answers.get(item["id"], "Not Answered")
        correct_ans = item["correct"]
        is_correct = (user_ans == correct_ans)

        status = "✅ Correct" if is_correct else "❌ Incorrect"
        color = "#28a745" if is_correct else "#dc3545"

        feedback_rows += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;"><b>{q_text}</b></td>
            <td style="padding: 10px; color: {color};"><b>{user_ans}</b></td>
            <td style="padding: 10px; color: #28a745;"><b>{correct_ans}</b></td>
            <td style="padding: 10px; color: {color};"><b>{status}</b></td>
        </tr>
        """

    html_template = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>🌿 RU Botany Challenge - Performance Report</h2>
        <p>Dear <b>{user_name}</b>,</p>
        <p>Thank you for completing the quiz! Here is your performance summary:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; margin-bottom: 20px;">
            <p style="margin: 5px 0;"><b>Participant Name:</b> {user_name}</p>
            <p style="margin: 5px 0;"><b>Final Score:</b> {score} / 20</p>
            <p style="margin: 5px 0;"><b>Time Elapsed:</b> {duration} seconds</p>
        </div>

        <h3>Detailed Feedback & Answer Key</h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="background-color: #28a745; color: white;">
                    <th style="padding: 10px;">Question</th>
                    <th style="padding: 10px;">Your Answer</th>
                    <th style="padding: 10px;">Correct Answer</th>
                    <th style="padding: 10px;">Result</th>
                </tr>
            </thead>
            <tbody>
                {feedback_rows}
            </tbody>
        </table>

        <br>
        <hr>
        <p style="font-size: 12px; color: #6c757d;">
            RU Botany Challenge | Created by {author_name} ({author_affiliation})
        </p>
    </body>
    </html>
    """

    html_body = html_template.format(
        user_name=user_name,
        score=score,
        duration=duration,
        feedback_rows=feedback_rows,
        author_name=AUTHOR_NAME,
        author_affiliation=AUTHOR_AFFILIATION
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False


def is_valid_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None


# ---------------------------
# Session State Initialization
# ---------------------------
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "duration" not in st.session_state:
    st.session_state.duration = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# ---------------------------
# UI Page Header
# ---------------------------
st.title("🌿 RU Botany Challenge")

# ---------------------------
# Step 1: Participant Registration
# ---------------------------
if not st.session_state.quiz_started:
    st.subheader("📋 Participant Registration")
    st.write("Please enter your details to start the quiz. Results will be emailed to you and added to the leaderboard.")

    with st.form("login_form"):
        name_input = st.text_input("Full Name / Student ID *")
        email_input = st.text_input("Email Address *")
        start_btn = st.form_submit_button("Start Quiz 🚀")

        if start_btn:
            if not name_input.strip():
                st.error("Name is required!")
            elif not email_input.strip():
                st.error("Email is required!")
            elif not is_valid_email(email_input.strip()):
                st.error("Please enter a valid email address!")
            else:
                st.session_state.user_name = name_input.strip()
                st.session_state.user_email = email_input.strip()
                st.session_state.start_time = time.time()
                st.session_state.quiz_started = True
                st.rerun()

# ---------------------------
# Step 2: Quiz Questions
# ---------------------------
elif st.session_state.quiz_started and not st.session_state.submitted:
    st.info(f"Participant: **{st.session_state.user_name}** ({st.session_state.user_email})")
    st.subheader("Answer all 20 questions:")

    user_answers = {}
    for item in QUIZ_DATA:
        user_answers[item["id"]] = st.radio(
            item["question"], 
            item["options"], 
            key=item["id"]
        )

    if st.button("Submit Answers"):
        end_time = time.time()
        st.session_state.duration = round(end_time - st.session_state.start_time, 2)
        st.session_state.user_answers = user_answers

        # Calculate score
        st.session_state.score = sum(
            [1 for item in QUIZ_DATA if user_answers.get(item["id"]) == item["correct"]]
        )

        # Save result to CSV for leaderboard
        df = load_data()
        new_entry = pd.DataFrame(
            [[st.session_state.user_name, st.session_state.user_email, st.session_state.score, st.session_state.duration]],
            columns=["Name", "Email", "Score", "Time"]
        )
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)

        # Dispatch detailed email feedback
        email_sent = send_feedback_email(
            recipient_email=st.session_state.user_email,
            user_name=st.session_state.user_name,
            score=st.session_state.score,
            duration=st.session_state.duration,
            user_answers=user_answers
        )

        st.session_state.submitted = True
        st.session_state.email_sent = email_sent
        st.rerun()

# ---------------------------
# Step 3: Immediate Feedback
# ---------------------------
elif st.session_state.submitted:
    st.success(
        f"✅ Quiz Submitted! Score: **{st.session_state.score} / 20** | "
        f"Time Taken: **{st.session_state.duration} seconds**"
    )

    if getattr(st.session_state, "email_sent", False):
        st.info(f"📧 A detailed result report has been sent to **{st.session_state.user_email}**.")
    else:
        st.warning("⚠️ Could not send the email automatically. Check your server SMTP credentials.")

    st.subheader("📊 Your Answer Feedback")

    for item in QUIZ_DATA:
        q_id = item["id"]
        q_text = item["question"]
        user_ans = st.session_state.user_answers.get(q_id, "Not Answered")
        correct_ans = item["correct"]

        if user_ans == correct_ans:
            st.markdown(f"**{q_text}**")
            st.success(f"Your Answer: {user_ans} (Correct)")
        else:
            st.markdown(f"**{q_text}**")
            st.error(f"Your Answer: {user_ans} | Correct Answer: {correct_ans}")

    if st.button("Take Quiz Again 🔄"):
        st.session_state.quiz_started = False
        st.session_state.submitted = False
        st.rerun()

# ---------------------------
# Leaderboard Table
# ---------------------------
st.markdown("---")
st.subheader("🏆 Leaderboard")

df_results = load_data()

if not df_results.empty:
    # Sort by highest score first, then by fastest time taken
    df_sorted = df_results.sort_values(
        by=["Score", "Time"],
        ascending=[False, True]
    ).reset_index(drop=True)

    df_sorted["Rank"] = df_sorted.index + 1

    def medal(rank):
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        return ""

    df_sorted["🏅"] = df_sorted["Rank"].apply(medal)

    # Rename columns for clear display in table
    df_display = df_sorted[["Rank", "🏅", "Name", "Email", "Score", "Time"]]
    df_display.columns = ["Rank", "Medal", "Participant Name", "Email Address", "Score (out of 20)", "Time Taken (sec)"]

    st.dataframe(df_display, use_container_width=True, height=400)
else:
    st.info("No participants on the leaderboard yet. Be the first!")

# ---------------------------
# Footer / Author Attribution
# ---------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; font-size: 14px;'>
        🌿 <b>RU Botany Challenge</b> Platform <br>
        Developed & Maintained by <b>{AUTHOR_NAME}</b> <br>
        <i>{AUTHOR_TITLE}</i> <br>
        {AUTHOR_AFFILIATION}
    </div>
    """,
    unsafe_allow_html=True
)
