import streamlit as st
import matplotlib.pyplot as plt
from auth import authenticate
from utils import predict_and_explain
from database import save_patient, load_patients


# ================= PAGE CONFIG =================
st.set_page_config(page_title="Explainable Diabetes AI", layout="centered")

# ================= GLOBAL CSS =================
st.markdown("""
<style>

/* Background */
.main {
     background: linear-gradient(135deg,#eef2ff,#ffffff);
}

h1,h2,h3 {
    color:#312e81;
    text-align:center;
}

.stButton>button {
    background:#4f46e5;
    color:white;
    border-radius:12px;
    height:3em;
    width:100%;
    font-size:18px;
    border:none;
}


/* Inputs */
.stNumberInput input {
    border-radius:10px;
}

/* LOGIN CARD */
.login-wrapper{
    display:flex;
    justify-content:center;
    align-items:center;
    height:80vh;
}

.login-card{
    display:flex;
    width:900px;
    background:white;
    border-radius:20px;
    box-shadow:0px 10px 30px rgba(0,0,0,0.15);
    overflow:hidden;
}

.left-panel{
    flex:1;
    background:linear-gradient(135deg,#a8c0ff,#3f2b96);
    color:white;
    padding:40px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
}

.right-panel{
    flex:1;
    padding:40px;
}

.title{
    text-align:center;
    font-size:28px;
    font-weight:bold;
    margin-bottom:20px;
}
.stApp {
    background: linear-gradient(135deg,#e3f2fd,#ffffff);
}

h1,h2,h3 {
    color:#0d47a1;
    text-align:center;
}

.stButton>button {
    background:#1976d2;
    color:white;
    border-radius:12px;
    height:3em;
    width:100%;
    font-size:18px;
    border:none;
}            

</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "login" not in st.session_state:
    st.session_state.login = False

default_patient = {
    "preg":0,"glu":0,"bp":0,"skin":0,"ins":0,"bmi":0.0,"dpf":0.0,"age":25
}

if "patient" not in st.session_state:
    st.session_state.patient = default_patient.copy()

# ================= LOGIN PAGE =================
if not st.session_state.login:

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #e0f2fe, #f3e8ff);
    }
    .login-box {
        background:white;
        padding:40px;
        border-radius:20px;
        box-shadow:0 20px 40px rgba(0,0,0,0.1);
    }
    .center-box {
        display:flex;
        justify-content:center;
        align-items:center;
        height:80vh;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5,6])

    # LEFT PANEL
    with col1:
        st.markdown("<div style='padding:3rem;text-align:center'>", unsafe_allow_html=True)
        st.markdown("## 🩺 Explainable AI")
        st.markdown("Transparent diabetes screening for clinical support")
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        st.markdown("### Doctor Login")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(user,pwd):
                st.session_state.login=True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("</div>", unsafe_allow_html=True)


# ================= MAIN APP =================
else:

    st.markdown("<h1>Explainable AI Diabetes Decision Support</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Transparent Clinical Risk Assessment Platform</h3>", unsafe_allow_html=True)

    # ================= PATIENT INPUT =================
    st.markdown("### 🩺 Patient Clinical Parameters")

    # ⭐ NEW — Patient identity
    patient_name = st.text_input("Patient Name")

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

    # ================= DATABASE TABLE =================
    st.subheader("📋 Patient Database")

    df = load_patients()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No patient records yet")

    # ================= PREDICT =================
    if st.button("Predict"):

        data = [preg,glu,bp,skin,ins,bmi,dpf,age]
        pred,prob,exp,shap_vals = predict_and_explain(data)

        # ================= RISK =================
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

        # ================= SAVE BUTTON (NEW) =================
        st.divider()

        if st.button("💾 Save Patient Record"):
            if patient_name.strip()=="":
                st.warning("Enter patient name before saving")
            else:
                save_patient(patient_name, age, glu, bp, bmi, user)
                st.success("Patient saved to database")

        # ================= LIFESTYLE =================
        st.subheader("Suggested lifestyle actions")
        st.write("- Reduce sugar intake")
        st.write("- 30 min daily walking")
        st.write("- Replace white rice with millets")
        st.write("- Regular glucose monitoring")

        # ================= CONTRIBUTION =================
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
