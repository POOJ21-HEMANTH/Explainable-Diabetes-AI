import pandas as pd
from datetime import datetime

from config import DB_FILE


def save_patient(name, age, glucose, bp, bmi, doctor):

    try:
        df = pd.read_csv(DB_FILE)
    except:
        df = pd.DataFrame(columns=["Name","Age","Glucose","BP","BMI","Doctor","Timestamp"])

    new_row = {
        "Name":name,
        "Age":age,
        "Glucose":glucose,
        "BP":bp,
        "BMI":bmi,
        "Doctor":doctor,
        "Timestamp":datetime.now()
    }

    df = pd.concat([df,pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)


def load_patients():
    try:
        return pd.read_csv(DB_FILE)
    except:
        return pd.DataFrame()
