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
.stApp {background:#f5f7ff;}
h1,h2,h3 {color:#1e1b4b;text-align:center;}
.stButton>button {
background:#4f46e5;color:white;border-radius:12px;height:3em;width:100%;
font-size:18px;border:none;box-shadow:0px 6px 18px rgba(79,70,229,0.3);}
.stNumberInput input,.stTextInput input,.stSelectbox div[data-baseweb="select"]{
border-radius:10px;background:white;color:black;}
.block-container{background:white;padding:2rem;border-radius:18px;
box-shadow:0px 10px 25px rgba(0,0,0,0.08);}
label,p,span{color:black!important;}
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
                st.rerun()
            else:
                st.error("Invalid credentials")

# ================= MAIN APP =================
else:

    st.markdown("<h1>Explainable AI Diabetes Decision Support</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Transparent Clinical Risk Assessment Platform</h3>", unsafe_allow_html=True)

    # ================= PATIENT INPUT =================
    st.markdown("### 🩺 Patient Clinical Parameters")

    patient_name = st.text_input("Patient Name")
    gender = st.selectbox("Gender",["Male","Female"])

    p = st.session_state.patient

    if gender=="Female":
        preg = st.number_input("Pregnancies",0,20,value=p["preg"])
    else:
        preg = 0

    glu = st.number_input("Glucose (mg/dL)",0,300)
    bp = st.number_input("Blood Pressure systolic (mmHg)",0,250)
    skin = st.number_input("Skin Thickness",0,100,value=p["skin"])
    ins = st.number_input("Insulin (µIU/mL)",0,900)
    bmi = st.number_input("BMI",0.0,70.0,value=p["bmi"])
    dpf = st.number_input("Family History Score",0.0,2.5,value=p["dpf"])
    age = st.number_input("Age",1,120,value=p["age"])
    history = st.selectbox("Known diabetes history",["No","Yes"])

    # ================= DATABASE =================
    st.subheader("📋 Patient Database")
    df = load_patients()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        selected = st.selectbox("Select patient to view", df["Name"])
        if st.button("View Selected Patient"):
            row = df[df["Name"]==selected].iloc[0]
            st.info(f"{row['Name']} | Age {row['Age']} | Date {row['Date']}")

    else:
        st.info("No patient records yet")

    # ================= PREDICT =================
    if st.button("Predict"):

        data = [preg,glu,bp,skin,ins,bmi,dpf,age]
        pred,prob,exp,shap_vals = predict_and_explain(data)

        # ⭐ Popup style
        with st.expander("🔍 View AI Diagnosis Report", expanded=True):

            st.header("Clinical Risk Assessment")

            if history=="Yes":
                st.error("Known Diabetes Case → Monitoring Mode")
            else:
                if prob < 0.35:
                    st.success(f"Healthy / Low Risk ({prob*100:.1f}%)")
                elif prob < 0.65:
                    st.warning(f"Moderate Risk ({prob*100:.1f}%)")
                else:
                    st.error(f"High Diabetes Risk ({prob*100:.1f}%)")

            # ================= EXPLANATION =================
            st.subheader("Why this prediction?")

            for f,v in exp:

                if f=="Glucose":
                    msg="Elevated glucose indicates impaired insulin regulation"
                elif f=="BMI":
                    msg="Higher BMI suggests obesity-related insulin resistance"
                elif f=="Age":
                    msg="Age increases metabolic risk"
                elif f=="DiabetesPedigreeFunction":
                    msg="Family history contributes to genetic susceptibility"
                elif f=="BloodPressure":
                    msg="Hypertension correlates with metabolic syndrome"
                else:
                    msg="Clinical feature contributing to prediction"

                if v>0:
                    st.write(f"🔴 {f}: {msg}")
                else:
                    st.write(f"🟢 {f}: Protective influence")

            # ================= SAVE =================
            st.divider()

            if st.button("💾 Save Patient Record"):
                if patient_name.strip()=="":
                    st.warning("Enter patient name")
                else:
                    save_patient(patient_name, age, glu, bp, bmi, user,
                                 datetime.now().strftime("%Y-%m-%d"))
                    st.success("Patient saved")

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
