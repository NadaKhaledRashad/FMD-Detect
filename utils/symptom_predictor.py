from pathlib import Path
import pandas as pd
import joblib

# =====================
# PROJECT PATH
# =====================

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

# =====================
# LOAD MODELS
# =====================

stack_model = joblib.load(
    MODELS_DIR / "fmd_model_stacking (1).pkl"
)

encoder_dict = joblib.load(
    MODELS_DIR / "fmd_encoders (2).pkl"
)

animal_cols = joblib.load(
    MODELS_DIR / "fmd_animal_cols (2).pkl"
)

FINAL_THRESHOLD = joblib.load(
    MODELS_DIR / "fmd_threshold (2).pkl"
)
# =====================
# PREDICTION FUNCTION
# =====================

def predict_symptoms(answers):

    print(answers)

    animal_type = answers.get("animal_type", "Cattle")

    fever = 1 if answers.get("fever", "").lower() == "yes" else 0

    salivation = 1 if answers.get("salivation", "").lower() == "yes" else 0

    mouth_lesions = 1 if answers.get("mouth_lesions", "").lower() == "yes" else 0

    lameness = 1 if answers.get("lameness", "").lower() == "yes" else 0

    hoof_lesions = 1 if answers.get("hoof_lesions", "").lower() == "yes" else 0

    chewing_problem = (
    1 if answers.get("chewing_problem", "").lower() == "yes" else 0
)
    mucous_abnormal = 1 if answers.get("mucous_abnormal", "").strip().lower() == "yes" else 0

    skin_turgor_abnormal = 1 if answers.get("skin_turgor_abnormal", "").strip().lower() == "yes" else 0

    body_swelling = 1 if answers.get("body_swelling", "").strip().lower() == "yes" else 0

    nasal_lesion = 1 if answers.get("nasal_lesion", "").strip().lower() == "yes" else 0
    high_risk_flag = 1 if (
        mouth_lesions == 1 or hoof_lesions == 1
    ) else 0

    pyrexic_flag = fever

    animal_encoded = encoder_dict[
        "Animal type"
    ].transform([[animal_type]])

    animal_df = pd.DataFrame(
        animal_encoded,
        columns=animal_cols
    )

    input_data = pd.DataFrame([{
        "Clinical manifestations/Drooling saliva":
            salivation,

        "Clinical manifestations/Lameness":
            lameness,

        "Clinical manifestations/Oral ulcer":
            mouth_lesions,

        "Clinical manifestations/Grinding teeth":
            chewing_problem,

        "Clinical manifestations/Lesions on the limbs":
            hoof_lesions,

        "pyrexic_flag":
            pyrexic_flag,

        "high_risk_flag":
            high_risk_flag,

        "mucous_abnormal":
            mucous_abnormal,

        "skin_turgor_abnormal":
            skin_turgor_abnormal,

        "body_swelling":
            body_swelling,

        "nasal_lesion":
            nasal_lesion
    }])

    for col in animal_cols:

        input_data[col] = animal_df[col].values[0]
        
    probability = stack_model.predict_proba(
        input_data
    )[0][1]
    

    return float(probability)