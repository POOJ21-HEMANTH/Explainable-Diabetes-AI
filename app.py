import streamlit as st
import matplotlib.pyplot as plt
from auth import authenticate
from utils import predict_and_explain
from database import save_patient, load_patients

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Explainable Diabetes AI", layout="wide")

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.stApp {background:#f5f7ff;}
h1,h2,h3 {color:#1e1b4b;text-align:center;}
.stButton>button {
    background:#4f46e5;color:white;border-radius:12px;
    height:3em;width:100%;font-size:18px;border:none;
    box-shadow:0px 6px 18px rgba(79,70,229,0.3);}
.stButton>button:hover {background:#4338ca;}
.stNumberInput input,.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius:10px;background:white;color:black;}
.block-container {
    background:white;padding:2rem;border-radius:18px;
    box-shadow:0px 10px 25px rgba(0,0,0,0.08);}
label,p,span {color:black !important;}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login=False

if "predict_done" not in st.session_state:
    st.session_state.predict_done=False

# ================= LOGIN =================
if not st.session_state.login:

    col1,col2=st.columns([1.2,1])

    with col1:
        st.markdown("## 🩺 Explainable AI")
        st.markdown("### Clinical Decision Support")
        st.write("Transparent diabetes screening platform for healthcare professionals.")

    with col2:
        st.markdown("### Doctor Login")
        user=st.text_input("Username")
        pwd=st.text_input("Password",type="password")

        if st.button("Login"):
            if authenticate(user,pwd):
                st.session_state.login=True
                st.session_state.user=user
                st.rerun()
            else:
                st.error("Invalid credentials")

# ================= DASHBOARD =================
else:

    user=st.session_state.user

    # ===== SIDEBAR =====
    st.sidebar.title("👨‍⚕️ Doctor Panel")
    menu=st.sidebar.radio("Navigation",["New Assessment","Patient Records","About"])

    st.sidebar.success(f"Logged in as {user}")

    # ================= ABOUT =================
    if menu=="About":
        st.title("Explainable Diabetes AI")
        st.write("""
        This system provides transparent AI-based diabetes risk assessment.
        Features include:
        - Risk prediction
        - Explainable reasoning
        - Clinical lifestyle suggestions
        - Patient record management
        """)

    # ================= PATIENT RECORDS =================
    if menu=="Patient Records":
        st.title("📋 Patient Database")

        df=load_patients()

        if not df.empty:
            st.dataframe(df,use_container_width=True)
        else:
            st.info("No patient records yet")

    # ================= NEW ASSESSMENT =================
    if menu=="New Assessment":

        st.title("New Clinical Assessment")

        patient_name=st.text_input("Patient Name")

        col1,col2=st.columns(2)

        with col1:
            preg=st.number_input("Pregnancies",0,20)
            glu=st.number_input("Glucose",0,300)
            bp=st.number_input("Blood Pressure",0,200)
            skin=st.number_input("Skin Thickness",0,100)

        with col2:
            ins=st.number_input("Insulin",0,900)
            bmi=st.number_input("BMI",0.0,70.0)
            dpf=st.number_input("Family History Score",0.0,2.5)
            age=st.number_input("Age",1,120)

        history=st.selectbox("Known diabetes history",["No","Yes"])

        # ===== PREDICT =====
        if st.button("Predict"):

            data=[preg,glu,bp,skin,ins,bmi,dpf,age]
            pred,prob,exp,shap_vals=predict_and_explain(data)

            st.session_state.predict_done=True
            st.session_state.last_result=(prob,exp,shap_vals)

        # ===== DISPLAY RESULT =====
        if st.session_state.predict_done:

            prob,exp,shap_vals=st.session_state.last_result

            st.header("Clinical Risk Assessment")

            if history=="Yes":
                st.error("Known Diabetes Case → Monitoring Mode")
            else:
                if prob<0.35:
                    st.success(f"Healthy / Low Risk ({prob*100:.1f}%)")
                elif prob<0.65:
                    st.warning(f"Moderate Risk ({prob*100:.1f}%)")
                else:
                    st.error(f"High Diabetes Risk ({prob*100:.1f}%)")

            # ===== EXPLANATION =====
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

            # ===== SAVE =====
            if st.button("💾 Save Patient Record"):
                if patient_name.strip()=="":
                    st.warning("Enter patient name")
                else:
                    save_patient(patient_name,age,glu,bp,bmi,user)
                    st.success("Patient saved")

            # ===== LIFESTYLE =====
            st.subheader("Suggested lifestyle actions")
            st.write("- Reduce sugar intake")
            st.write("- 30 min daily walking")
            st.write("- Replace white rice with millets")
            st.write("- Regular glucose monitoring")

            # ===== CHART =====
            st.subheader("Feature Contribution")
            names=[x[0] for x in exp]
            vals=[x[1] for x in exp]
            fig,ax=plt.subplots()
            ax.barh(names,vals)
            st.pyplot(fig)

            # ===== SHAP =====
            st.subheader("SHAP Impact")
            feature_names=["Pregnancies","Glucose","BloodPressure","SkinThickness",
            "Insulin","BMI","DiabetesPedigreeFunction","Age"]
            fig2,ax2=plt.subplots()
            ax2.barh(feature_names,shap_vals)
            st.pyplot(fig2)
