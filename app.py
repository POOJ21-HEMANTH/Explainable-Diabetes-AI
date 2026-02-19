import streamlit as st
import matplotlib.pyplot as plt
from auth import authenticate
from utils import predict_and_explain
import shap

st.set_page_config(page_title="Explainable Diabetes AI")

# ================= SESSION STATE =================

if "login" not in st.session_state:
    st.session_state.login = False

# patient data persistence
default_patient = {
    "preg":0,"glu":0,"bp":0,"skin":0,"ins":0,"bmi":0.0,"dpf":0.0,"age":25
}

if "patient" not in st.session_state:
    st.session_state.patient = default_patient.copy()

# ================= LOGIN =================

if not st.session_state.login:

    st.title("Doctor Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(user,pwd):
            st.session_state.login = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ================= MAIN APP =================

else:

    st.title("Explainable Diabetes Decision Support")

    st.subheader("Patient Data Entry")
    st.markdown("### Demo Patients")

    col1,col2,col3 = st.columns(3)

    if col1.button("Healthy Adult"):
        st.session_state.patient = {
            "preg":1,"glu":90,"bp":70,"skin":20,"ins":80,"bmi":22.0,"dpf":0.3,"age":30
        }

    if col2.button("High Risk"):
        st.session_state.patient = {
            "preg":4,"glu":165,"bp":88,"skin":35,"ins":250,"bmi":33.5,"dpf":0.8,"age":52
        }

    if col3.button("Known Diabetic"):
        st.session_state.patient = {
            "preg":6,"glu":180,"bp":95,"skin":40,"ins":300,"bmi":35.2,"dpf":1.1,"age":58
        }

    # ================= INPUTS =================

    p = st.session_state.patient

    preg = st.number_input("Pregnancies",0,20,value=p["preg"])
    glu = st.number_input("Glucose",0,300,value=p["glu"])
    bp = st.number_input("Blood Pressure",0,200,value=p["bp"])
    skin = st.number_input("Skin Thickness",0,100,value=p["skin"])
    ins = st.number_input("Insulin",0,900,value=p["ins"])
    bmi = st.number_input("BMI",0.0,70.0,value=p["bmi"])
    dpf = st.number_input("Family History Score",0.0,2.5,value=p["dpf"])
    age = st.number_input("Age",1,120,value=p["age"])

    history = st.selectbox("Known diabetes history",["No","Yes"])

    # ================= PREDICT =================

    if st.button("Predict"):

        if history=="Yes":
            st.warning("Patient has known diabetes → system focusing on risk monitoring and lifestyle guidance")

        data = [preg,glu,bp,skin,ins,bmi,dpf,age]

        pred,prob,exp,shap_vals = predict_and_explain(data)

        # ================= RESULT =================

        st.header("Prediction")

        if pred==1:
            st.error(f"High Diabetes Risk ({prob*100:.1f}%)")
        else:
            st.success(f"Low Diabetes Risk ({prob*100:.1f}%)")

        # ================= LIME TEXT =================

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

        # ================= LIFESTYLE =================

        st.subheader("Suggested lifestyle actions")
        st.write("- Reduce sugar intake")
        st.write("- 30 min daily walking")
        st.write("- Replace white rice with millets")
        st.write("- Regular glucose monitoring")

        # ================= LIME BAR =================

        st.subheader("Feature Contribution Visualization")

        names=[x[0] for x in exp]
        vals=[x[1] for x in exp]

        fig,ax=plt.subplots()
        ax.barh(names,vals)
        st.pyplot(fig)

        # ================= SHAP =================

        st.subheader("SHAP Explanation (Feature Impact)")

        feature_names = [
        "Pregnancies","Glucose","BloodPressure","SkinThickness",
        "Insulin","BMI","DiabetesPedigreeFunction","Age"
        ]

        fig2, ax2 = plt.subplots()
        ax2.barh(feature_names, shap_vals)
        st.pyplot(fig2)
