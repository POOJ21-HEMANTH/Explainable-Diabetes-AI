import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from config import APP_NAME

import os

load_dotenv()

from datetime import datetime
from auth import authenticate
from utils import predict_and_explain
from database import save_patient, load_patients
st.caption(APP_NAME)

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Explainable Diabetes AI", layout="centered")

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.stApp {
    background: #f5f7ff;
}

/* Force most text to black */
h1, h2, h3, h4, h5, h6,
p, span, div, label, li, a:not(.stButton a),
.stMarkdown, .stText, .stCaption,
.block-container, .stApp * {
    color: #000000 !important;
}

/* Headings centered */
h1, h2, h3 {
    text-align: center;
}

/* Buttons - keep white text */
.stButton > button {
    background: #4f46e5;
    color: white !important;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
    box-shadow: 0px 6px 18px rgba(79,70,229,0.3);
}

/* Text inputs & number inputs - black text */
.stNumberInput input,
.stTextInput input {
    border-radius: 10px;
    background: white;
    color: #000000 !important;
}

/* ── Selectbox: yellow text for selected value + dropdown options ── */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
    background: white;
}

/* Selected value (the box you see before clicking) */
.stSelectbox [data-baseweb="select"] > div {
    color: #ffff00 !important;   /* bright yellow */
}

/* Dropdown menu options when opened */
.stSelectbox ul[data-baseweb="menu"] li,
.stSelectbox [role="option"] {
    color: #ffff00 !important;   /* yellow for each option */
    background: #1a1a1a !important;  /* dark background so yellow is readable */
}

/* Optional: make the selected/hovered option more visible */
.stSelectbox [role="option"]:hover,
.stSelectbox [aria-selected="true"] {
    background: #333333 !important;
    color: #ffff00 !important;
}

/* Main content blocks */
.block-container {
    background: white;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
}

/* Extra override for markdown / any leftover colored text */
.stApp [data-testid="stMarkdownContainer"] * {
    color: #000000 !important;
}

label, p, span {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "login" not in st.session_state:
    st.session_state.login = False

default_patient = {"preg":0,"glu":0,"bp":0,"skin":0,"ins":0,"bmi":0.0,"dpf":0.0,"age":25}

if "patient" not in st.session_state:
    st.session_state.patient = default_patient.copy()

# ================= LOGIN PAGE =================
if not st.session_state.login:
    st.markdown("""
<style>
.stApp {
    background-image: url("https://img.freepik.com/free-vector/watercolor-medical-background_52683-162142.jpg?semt=ais_user_personalization&w=740&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* dark overlay so text visible */
.stApp::before {
    content:"";
    position:fixed;
    top:0;left:0;
    width:100%;height:100%;
    background:rgba(0,0,0,0.35);
    z-index:-1;
}
</style>
""", unsafe_allow_html=True)

    col1,col2 = st.columns([5,6])

    with col1:
        st.markdown("## 🩺 Explainable AI")
        st.markdown("Transparent diabetes screening for clinical support")

    with col2:
        st.markdown("### Doctor Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(user,pwd):
                st.session_state.login=True
                st.session_state.doctor = user
                st.rerun()
            else:
                st.error("Invalid credentials")

# ================= MAIN APP =================
else:
    st.markdown("<h1>Explainable AI Diabetes Decision Support</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Transparent Clinical Risk Assessment Platform</h3>", unsafe_allow_html=True)

    st.markdown("### 🩺 Patient Clinical Parameters")
    
    # ================= INPUTS =================
    patient_name = st.text_input("Patient Name")
    age = st.number_input("Age",1,120)

    gender = st.selectbox("Gender",["Male","Female","Other"])

    if gender=="Female":
        preg = st.number_input("Pregnancy history",0,15)
    else:
        preg = 0

    height = st.number_input("Height (cm)",100,220)
    weight = st.number_input("Weight (kg)",30,200)

    bmi = weight / ((height/100)**2)
    st.write(f"Calculated BMI: {bmi:.2f}")

    glu = st.number_input("Glucose (mg/dL)",0,300)
    bp = st.number_input("Blood Pressure systolic (mmHg)",0,250)
    ins = st.number_input("Insulin (µIU/mL)",0,900)
    skin = st.number_input("Skin thickness (optional)",0,100,value=20)

    family_history = st.selectbox("Family history of diabetes",["No","Yes"])
    dpf = 1.0 if family_history=="Yes" else 0.2

    # ================= DATABASE TABLE =================
    st.subheader("📋 Patient Database")

    df = load_patients()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No patient records yet")

    # ================= PREDICT BUTTON =================
    if st.button("Predict"):

        data = [preg,glu,bp,skin,ins,bmi,dpf,age]

        pred,prob,exp,shap_vals = predict_and_explain(data)

        # ⭐ store prediction
        st.session_state.prediction_data = (pred,prob,exp,shap_vals)

    # ================= SHOW RESULTS =================
if "prediction_data" in st.session_state:
    pred,prob,exp,shap_vals = st.session_state.prediction_data
    # ================= RISK CARD =================
    risk_label = "Low Risk"
    risk_color = "#bbf7d0"

    if prob >= 0.65:
        risk_label = "High Risk"
        risk_color = "#fecaca"
    elif prob >= 0.35:
        risk_label = "Moderate Risk"
        risk_color = "#fde68a"

    st.markdown(f"""
    <div style="background:{risk_color};
    padding:18px;border-radius:14px;margin-top:10px;margin-bottom:10px;
    box-shadow:0px 6px 14px rgba(0,0,0,0.08)">
    <b>Risk Level:</b> {risk_label}<br>
    <b>Probability:</b> {prob*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

    st.header("Clinical Risk Assessment")

    if prob < 0.35:
        st.success(f"Healthy / Low Risk ({prob*100:.1f}%)")
    elif prob < 0.65:
        st.warning(f"Moderate Risk ({prob*100:.1f}%)")
    else:
        st.error(f"High Diabetes Risk ({prob*100:.1f}%)")
        # ================= AUTO EXPLANATION =================
        top_factors = [f for f,v in exp if v>0][:3]

        explanation_para = (
            f"The AI model estimates a {risk_label.lower()} diabetes risk primarily due to "
            f"{', '.join(top_factors)} influencing metabolic health. "
            f"These factors contribute to impaired glucose regulation and insulin response patterns."
        )

        st.subheader("AI Clinical Reasoning")
        st.info(explanation_para)
        # ================= CARE PLAN =================
        st.subheader("Suggested Care Plan")

        if prob < 0.35:
            st.success("Maintain healthy lifestyle")
            st.write("- Balanced diet")
            st.write("- Regular exercise")
            st.write("- Annual screening")

        elif prob < 0.65:
            st.warning("Preventive intervention recommended")
            st.write("- Reduce sugar intake")
            st.write("- Weight management")
            st.write("- Monthly glucose monitoring")

        else:
            st.error("Clinical follow-up recommended")
            st.write("- Consult physician")
            st.write("- HbA1c testing")
            st.write("- Structured diet plan")
            st.write("- Regular glucose monitoring")

            

        # ================= SAVE BUTTON (NOW WORKS) =================
        if st.button("💾 Save Patient Record"):

            if patient_name.strip()=="":
                st.warning("Enter patient name")
            else:
                doctor = st.session_state.get("doctor","unknown")
                save_patient(patient_name, age, glu, bp, bmi, doctor)
                st.success("Patient saved ✅")

                # refresh table
                st.session_state.pop("prediction_data")
                st.rerun()

            # ================= LIFESTYLE =================
            st.subheader("Suggested lifestyle actions")
            st.write("- Reduce sugar intake")
            st.write("- 30 min daily walking")
            st.write("- Replace white rice with millets")
            st.write("- Regular glucose monitoring")

            # ================= CHART =================
            st.subheader("Feature Contribution Visualization")
            names=[x[0] for x in exp]
            vals=[x[1] for x in exp]
            fig,ax=plt.subplots()
            ax.barh(names,vals)
            st.pyplot(fig)

            # ================= SHAP =================
            st.subheader("SHAP Explanation (Feature Impact)")
            feature_names=["Pregnancies","Glucose","BloodPressure","SkinThickness",
            "Insulin","BMI","DiabetesPedigreeFunction","Age"]
            fig2, ax2 = plt.subplots()
            ax2.barh(feature_names, shap_vals)
            st.pyplot(fig2)