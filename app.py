import streamlit as st
import matplotlib.pyplot as plt
from auth import authenticate
from utils import predict_and_explain

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Explainable Diabetes AI", layout="centered")

# ================= GLOBAL CSS =================
st.markdown("""
<style>

/* Background */
.main {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}

/* Titles */
h1,h2,h3 {
    color:white;
    text-align:center;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg,#00c6ff,#0072ff);
    color:white;
    border-radius:12px;
    height:3em;
    width:100%;
    font-size:18px;
    border:none;
    box-shadow:0px 4px 15px rgba(0,0,0,0.2);
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

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    # LEFT PANEL
    st.markdown("""
    <div class="left-panel">
        <h2>AI Clinical Support</h2>
        <p>Explainable diabetes screening for transparent medical decisions.</p>
    </div>
    """, unsafe_allow_html=True)

    # RIGHT PANEL
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.markdown('<div class="title">Doctor Login</div>', unsafe_allow_html=True)

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(user,pwd):
            st.session_state.login=True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown("</div></div></div>", unsafe_allow_html=True)

# ================= MAIN APP =================
else:

    st.markdown("<h1>Explainable AI Diabetes Decision Support</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Transparent Clinical Risk Assessment Platform</h3>", unsafe_allow_html=True)

    st.markdown("### 🩺 Patient Clinical Parameters")
    st.markdown("### Demo Patients")

    col1,col2,col3 = st.columns(3)

    if col1.button("Healthy Adult"):
        st.session_state.patient = {"preg":1,"glu":90,"bp":70,"skin":20,"ins":80,"bmi":22.0,"dpf":0.3,"age":30}

    if col2.button("High Risk"):
        st.session_state.patient = {"preg":4,"glu":165,"bp":88,"skin":35,"ins":250,"bmi":33.5,"dpf":0.8,"age":52}

    if col3.button("Known Diabetic"):
        st.session_state.patient = {"preg":6,"glu":180,"bp":95,"skin":40,"ins":300,"bmi":35.2,"dpf":1.1,"age":58}

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
