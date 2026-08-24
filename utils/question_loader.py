from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

QUESTION_FILE = BASE_DIR / "data" / "chatbot_questions.xlsx"

def load_questions():

    df = pd.read_excel(QUESTION_FILE)

    df.columns = df.columns.str.strip()

    questions = []

    for _, row in df.iterrows():

        q_type = str(row["Type"]).strip().lower()

        if q_type == "multiple_choice":

            options = [
                opt.strip()
                for opt in str(row["Options"]).split(",")
            ]

        else:

            options = []

        questions.append({
            "id": row["flutter doctor"],
            "field": row["Field_Name"],
            "question": row["Question"],
            "type": q_type,
            "options": options,
            "weight": row["Weight"],
            "category": row["Category"]
        })

    return questions