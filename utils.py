import joblib
import numpy as np
import shap


model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
explainer = shap.LinearExplainer(model, scaler.transform([[0]*8]))

features = [
    "Pregnancies","Glucose","BloodPressure","SkinThickness",
    "Insulin","BMI","DiabetesPedigreeFunction","Age"
]

def predict_and_explain(input_data):

    X = np.array(input_data).reshape(1,-1)
    X_scaled = scaler.transform(X)

    prob = model.predict_proba(X_scaled)[0][1]
    prediction = model.predict(X_scaled)[0]

    # SHAP values
    shap_values = explainer.shap_values(X_scaled)[0]

    explanation = []
    for f,val in zip(features, shap_values):
        explanation.append((f,val))

    explanation = sorted(explanation, key=lambda x: abs(x[1]), reverse=True)

    return prediction, prob, explanation[:5], shap_values

