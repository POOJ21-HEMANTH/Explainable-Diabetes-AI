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
    /* Main container background */
    .stApp { background-color: #f8fafc; }
    
    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .metric-title { color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem; }
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
                st.session_state.doctor = user
                st.rerun()
            else:
                st.error("Invalid credentials")

else:
    # Header area with actions
    head1, head2 = st.columns([3, 1])
    with head1:
        st.title("Clinical Decision Support")
        st.caption("Real-time risk assessment and AI explainability for diabetic patients.")
    with head2:
        st.write("") # Spacing
        if st.button("🚀 Run Prediction"):
            # Trigger prediction logic
            data = [preg, glu, bp, skin, ins, bmi, dpf, age]
            st.session_state.prediction_data = predict_and_explain(data)

    # CREATE TWO MAIN COLUMNS: Left (Inputs) | Right (Results)
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### 🩺 Patient Clinical Parameters")
        # Use a nested grid for inputs
        i1, i2, i3 = st.columns(3)
        with i1:
            patient_name = st.text_input("Patient Name")
            height = st.number_input("Height (cm)", 100, 220)
        with i2:
            age = st.number_input("Age", 1, 120)
            weight = st.number_input("Weight (kg)", 30, 200)
        with i3:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            bmi = weight / ((height/100)**2)
            st.text_input("Calculated BMI", f"{bmi:.1f}", disabled=True)

        # AI Reasoning Section (Below inputs)
        st.markdown("### 🧠 AI Clinical Reasoning")
        if "prediction_data" in st.session_state:
            pred, prob, exp, shap_vals = st.session_state.prediction_data
            top_factors = [f for f, v in exp if v > 0][:3]
            st.info(f"The model identifies **{', '.join(top_factors)}** as the primary contributing factors.")
        else:
            st.info("Run prediction to see AI reasoning")

    with right_col:
        st.markdown("### 📊 Assessment Result")
        if "prediction_data" in st.session_state:
            pred, prob, exp, shap_vals = st.session_state.prediction_data
            
            # Use a colorful metric display
            st.metric(label="Diabetes Probability", value=f"{prob*100:.1f}%")
            
            st.markdown("### 📋 Suggested Care Plan")
            if prob < 0.35:
                st.success("Low Risk: Maintain lifestyle")
            elif prob < 0.65:
                st.warning("Moderate Risk: Preventive intervention")
            else:
                st.error("High Risk: Clinical follow-up")
        else:
            st.write("Waiting for prediction data...")

    # Patient History Table (Full width at bottom)
    st.markdown("--- ")
    st.subheader("📋 Patient Record History")
    df = load_patients()
    st.dataframe(df, use_container_width=True)

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
