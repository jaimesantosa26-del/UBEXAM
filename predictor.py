import streamlit as st
import pandas as pd
from catboost import CatBoostClassifier

st.set_page_config(page_title="Customer Churn Predictor", layout="wide")
st.title("💳 Credit Card Customer Churn Prediction")

# --------------------------
# Upload Dataset
# --------------------------
uploaded_file = st.file_uploader("Upload preprocessed CSV dataset", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Normalize column names: lowercase, no spaces
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    st.write("### Dataset Columns")
    st.write(df.columns.tolist())

    TARGET = "attritionflag"
    if TARGET not in df.columns:
        st.error(f"Target '{TARGET}' not in dataset!")
    else:
        X = df.drop(columns=[TARGET])
        y = df[TARGET]
        model_features = X.columns.tolist()

        # --------------------------
        # Train CatBoost
        # --------------------------
        model = CatBoostClassifier(iterations=300, depth=4, learning_rate=0.05, verbose=0, random_state=42)
        model.fit(X, y)
        st.success("✅ Model trained on uploaded dataset!")

        # --------------------------
        # User Input for Prediction
        # --------------------------
        st.subheader("Enter customer info for prediction")
        age = st.number_input("Age", 18, 100, 30)
        income = st.number_input("Income", 0.0, 1e7, 50000.0)
        total_txn = st.number_input("Total Transactions", 0, 1000, 10)
        total_spend = st.number_input("Total Spend", 0.0, 1e6, 5000.0)
        tenure = st.number_input("Tenure (months)", 0, 120, 12)
        marital_status = st.selectbox("Marital Status", ["married","single","divorced","widowed"])
        education = st.selectbox("Education Level", ["high_school","bachelor","master","phd"])

        # Build input dataframe
        input_df = pd.DataFrame({
            'age':[age],
            'income':[income],
            'totaltransactions':[total_txn],
            'totalspend':[total_spend],
            'tenure':[tenure],
            'txntotenureratio':[total_txn/tenure if tenure>0 else total_txn],
            'spendpertxn':[total_spend/total_txn if total_txn>0 else 0],
            'maritalstatus_widowed':[1 if marital_status=='widowed' else 0],
            'educationlevel_high_school':[1 if education=='high_school' else 0],
            'educationlevel_master':[1 if education=='master' else 0],
            'age_bucket_low':[1 if age<=25 else 0],
            'tenuregroup_6m':[1 if tenure<=6 else 0],
            # leave 'creditlimit_bucket_low' as 0, it exists in training already
            'creditlimit_bucket_low':[0],
        })

        # Align input columns to model features
        for col in model_features:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model_features]

        if st.button("Predict Attrition"):
            pred = model.predict(input_df)[0]
            proba = model.predict_proba(input_df)[0][1]
            st.write(f"**Predicted Attrition:** {'Yes' if pred==1 else 'No'}")
            st.write(f"**Probability of Churn:** {proba:.2%}")
