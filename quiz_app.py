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
# Replace these values with your details!
AUTHOR_NAME = "Your Name"                # e.g., "Manosh Biswas, PhD"
AUTHOR_TITLE = "Your Position/Title"    # e.g., "Assistant Professor" or "Botany Student"
AUTHOR_AFFILIATION = "Your Department / Institution"  # e.g., "Department of Botany, Rajshahi University"

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
        is_correct = user_ans == correct_ans

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

    html_body = f"""
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
                <tr style
