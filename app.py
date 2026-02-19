import streamlit as st
import matplotlib.pyplot as plt
from auth import authenticate
from utils import predict_and_explain
from database import save_patient, load_patients

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Explainable Diabetes AI", layout="wide")

# ================= GLOBAL CSS =================
# ── Global modern medical style ────────────────────────────────────────
st.markdown("""
<style>
    /* Background & typography */
    .stApp {
        background: #f8fafc;
    }
    h1, h2, h3, h4 {
        color: #1e293b;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .stMarkdown h1 {
        font-size: 2.4rem !important;
        margin-bottom: 0.4rem;
    }

    /* Card-like containers */
    .block-container, section.main > div {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        padding: 2.2rem 2.8rem;
        margin-bottom: 1.8rem;
    }

    /* Inputs & buttons */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 0.6rem 1rem;
    }
    .stButton > button {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(16,185,129,0.25);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #059669;
        box-shadow: 0 4px 16px rgba(16,185,129,0.35);
    }
    .stButton > button[kind="primary"] {
        background: #4f46e5 !important;
    }

    /* Sidebar improvements */
    [data-testid="stSidebar"] {
        background: #0f172a;
        color: white;
    }
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] a {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.4rem;
        margin: 0.3rem 0;
    }
    [data-testid="stSidebar"] .stRadio > div[aria-checked="true"] {
        background: #334155 !important;
    }

    /* Risk badges */
    .risk-low  { background:#d1fae5; color:#065f46; padding:1rem; border-radius:12px; font-weight:600; }
    .risk-mod  { background:#fef3c7; color:#92400e; padding:1rem; border-radius:12px; font-weight:600; }
    .risk-high { background:#fee2e2; color:#991b1b; padding:1rem; border-radius:12px; font-weight:600; }
    .risk-known{ background:#e0f2fe; color:#1e40af; padding:1rem; border-radius:12px; font-weight:600; }

    /* Hide Streamlit footer & header padding */
    footer {visibility: hidden;}
    .st-emotion-cache-1v0mbdj {padding-top: 2rem !important;}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login=False

if "predict_done" not in st.session_state:
    st.session_state.predict_done=False

# ================= LOGIN =================
if not st.session_state.get("login", False):

    # Optional: subtle background gradient
    st.markdown("""
    <style>
        .stApp { 
            background: linear-gradient(135deg, #e6f4f1 0%, #f0f9ff 100%); 
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='min-height:85vh; display:flex; align-items:center; justify-content:center; padding:1rem;'>", unsafe_allow_html=True)

    col_logo, col_form = st.columns([1, 1.3])

    with col_logo:
        st.markdown("""
        <div style="padding:2.5rem 1.5rem; text-align:center;">
            <div style="font-size:6.5rem; margin-bottom:1rem;">🩺</div>
            <h1 style="font-size:3.2rem; margin:0.3rem 0; color:#0f766e;">MedVerify</h1>
            <p style="color:#475569; font-size:1.25rem; line-height:1.5; max-width:380px; margin:0 auto;">
                Transparent AI-powered diabetes risk screening<br>
                <small>Built for clinical trust and explainability</small>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""
        <div style="background:white; padding:2.8rem 2.2rem; border-radius:16px; 
                    box-shadow:0 12px 40px rgba(0,0,0,0.14); border:1px solid #e2e8f0;">
            <h2 style="text-align:center; margin:0 0 2rem; color:#1e293b;">Doctor / Clinician Login</h2>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", "", key="login_user", placeholder="Enter your username")
        password = st.text_input(label="Password",value="",type="password",key="login_pass",placeholder="••••••••")

        if st.button("Secure Login", type="primary", use_container_width=True):
            if authenticate(username, password):
                st.session_state.login = True
                st.session_state.user = username
                st.success("Login successful — welcome back")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

        st.markdown("""
            <div style="text-align:center; margin-top:1.5rem; color:#64748b; font-size:0.95rem;">
                For authorized healthcare professionals only
            </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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

        st.markdown("<h1 style='text-align:center; color:#0f766e; margin-bottom:0.8rem;'>New Clinical Assessment</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#475569; margin-bottom:2.5rem;'>Enter patient parameters to receive explainable risk prediction</p>", unsafe_allow_html=True)

        with st.container():
            patient_name = st.text_input("**Patient Name** (required for saving)", "")

            st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

            col1, col2 = st.columns([1,1], gap="medium")

            with col1:
                st.markdown("#### Vital Signs & History")
                preg  = st.number_input("Pregnancies", 0, 20, 0, key="preg")
                glu   = st.number_input("Glucose (mg/dL)", 0, 300, 0, key="glu")
                bp    = st.number_input("Blood Pressure (mmHg)", 0, 200, 0, key="bp")
                skin  = st.number_input("Skin Thickness (mm)", 0, 100, 0, key="skin")

            with col2:
                st.markdown("#### Metabolic & Demographic")
                ins   = st.number_input("Insulin (mu U/mL)", 0, 900, 0, key="ins")
                bmi   = st.number_input("BMI (kg/m²)", 0.0, 70.0, 0.0, 0.1, key="bmi")
                dpf   = st.number_input("Diabetes Pedigree Function", 0.0, 2.5, 0.0, 0.01, key="dpf")
                age   = st.number_input("Age (years)", 1, 120, 25, key="age")

            history = st.selectbox("**Known diabetes history**", ["No", "Yes"])

        # ── Predict Button ───────────────────────────────────────
        st.markdown("<div style='text-align:center; margin:2.5rem 0 1.5rem;'>", unsafe_allow_html=True)
        if st.button("Run Risk Assessment →", type="primary", use_container_width=False):
            data = [preg, glu, bp, skin, ins, bmi, dpf, age]
            pred, prob, exp, shap_vals = predict_and_explain(data)

            st.session_state.predict_done = True
            st.session_state.last_result = (prob, exp, shap_vals)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Results ──────────────────────────────────────────────
        if st.session_state.predict_done:

            prob, exp, shap_vals = st.session_state.last_result

            st.markdown("---")

            st.markdown("<h3 style='color:#1e293b;'>Clinical Risk Assessment</h3>", unsafe_allow_html=True)

            if history == "Yes":
                st.markdown('<div class="risk-known">Known Diabetes Case → Enter Monitoring & Management Mode</div>', unsafe_allow_html=True)
            else:
                if prob < 0.35:
                    st.markdown(f'<div class="risk-low">Low Risk – {prob*100:.1f}% probability</div>', unsafe_allow_html=True)
                elif prob < 0.65:
                    st.markdown(f'<div class="risk-mod">Moderate Risk – {prob*100:.1f}% probability</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="risk-high">High Risk – {prob*100:.1f}% probability</div>', unsafe_allow_html=True)

            # Explanation – nicer formatting
            st.markdown("<h4 style='margin-top:2rem;'>Why this prediction? (Top contributing factors)</h4>", unsafe_allow_html=True)

            for f, v in exp:
                if f == "Glucose":
                    msg = "Elevated glucose indicates impaired insulin regulation"
                elif f == "BMI":
                    msg = "Higher BMI suggests obesity-related insulin resistance"
                elif f == "Age":
                    msg = "Age increases metabolic risk"
                elif f == "DiabetesPedigreeFunction":
                    msg = "Family history contributes to genetic susceptibility"
                elif f == "BloodPressure":
                    msg = "Hypertension correlates with metabolic syndrome"
                else:
                    msg = "Clinical feature contributing to prediction"

                icon = "🔴" if v > 0 else "🟢"
                direction = "increases risk" if v > 0 else "protective / lower risk"
                st.markdown(f"{icon} **{f}** ({v:+.3f}) — {msg} ({direction})")

            st.markdown("---")

            # Save + Lifestyle in columns
            c_save, c_life = st.columns([1, 1.4])

            with c_save:
                st.markdown("<h4>Save to Records</h4>", unsafe_allow_html=True)
                if st.button("💾 Save Patient Record", use_container_width=True):
                    if patient_name.strip() == "":
                        st.warning("Please enter Patient Name before saving")
                    else:
                        save_patient(patient_name, age, glu, bp, bmi, user)
                        st.success("Record saved successfully")

            with c_life:
                st.markdown("<h4>Recommended Lifestyle Actions</h4>", unsafe_allow_html=True)
                st.markdown("""
                - Reduce added sugar & refined carbohydrates  
                - Aim for 30–45 min brisk walking daily  
                - Prefer whole grains (millets, brown rice, oats)  
                - Monitor blood glucose regularly
                """)

            st.markdown("---")

            # Charts – better titles + colors
            st.markdown("<h4>Feature Importance & Impact</h4>", unsafe_allow_html=True)

            c_chart1, c_chart2 = st.columns(2, gap="medium")

            with c_chart1:
                st.caption("Top factors from local explanation")
                names = [x[0] for x in exp]
                vals  = [x[1] for x in exp]
                fig, ax = plt.subplots(figsize=(5, 4.2))
                colors = ["#ef4444" if v>0 else "#10b981" for v in vals]
                ax.barh(names, vals, color=colors)
                ax.axvline(0, color="#94a3b8", lw=0.8)
                ax.set_xlabel("Contribution to prediction")
                st.pyplot(fig)

            with c_chart2:
                st.caption("Global SHAP feature impact")
                feature_names = ["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"]
                fig2, ax2 = plt.subplots(figsize=(5, 5))
                colors2 = ["#ef4444" if v>0 else "#10b981" for v in shap_vals]
                ax2.barh(feature_names, shap_vals, color=colors2)
                ax2.axvline(0, color="#94a3b8", lw=0.8)
                ax2.set_xlabel("Average SHAP value (impact on model)")
                st.pyplot(fig)
