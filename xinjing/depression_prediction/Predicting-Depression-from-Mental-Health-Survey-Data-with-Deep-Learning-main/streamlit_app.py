import streamlit as st
import pandas as pd
import joblib
import tensorflow as tf
import numpy as np

# Configure the page
st.set_page_config(page_title="Depression Prediction App", layout="centered")

# Load the saved scaler and Keras model
scaler = joblib.load('scaler.pkl')
keras_model = tf.keras.models.load_model('keras_model.h5')

# App Title and Description
st.title("🧠 Depression Prediction App")
st.markdown("""
Welcome to the Depression Prediction App.  
Enter your personal details below, and the model will predict whether you are likely to be depressed.
""")

# User Input Form
with st.form("prediction_form", clear_on_submit=True):
    st.header("Enter Your Details")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=0.0, max_value=120.0, value=30.0, step=1.0)
        work_pressure = st.number_input("Work Pressure", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
        job_satisfaction = st.number_input("Job Satisfaction", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
        sleep_duration = st.number_input("Sleep Duration (hours)", min_value=0.0, max_value=24.0, value=7.0, step=0.1)
    with col2:
        work_or_study_hours = st.number_input("Work/Study Hours", min_value=0.0, max_value=24.0, value=8.0, step=0.1)
        financial_stress = st.number_input("Financial Stress", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
        gender = st.selectbox("Gender", options=["Male", "Female"])
        working_status = st.selectbox("Are you a working professional?", options=["Working Professional", "Student"])
        suicidal_thoughts = st.selectbox("Have you ever had suicidal thoughts?", options=["Yes", "No"])
    
    dietary_habits = st.selectbox("Dietary Habits", options=["Healthy", "Moderate", "Unhealthy"])
    family_history = st.selectbox("Family History of Mental Illness", options=["Yes", "No"])
    
    submit_button = st.form_submit_button("Predict")

# Process the form when submitted
if submit_button:
    # Map inputs to the expected numerical values
    gender_male = 1 if gender == "Male" else 0
    working_professional_val = 1 if working_status == "Working Professional" else 0
    suicidal_thoughts_val = 1 if suicidal_thoughts == "Yes" else 0
    family_history_val = 1 if family_history == "Yes" else 0
    
    # For dietary habits, we assume two dummy columns:
    if dietary_habits == "Healthy":
        dietary_moderate = 0
        dietary_unhealthy = 0
    elif dietary_habits == "Moderate":
        dietary_moderate = 1
        dietary_unhealthy = 0
    else:  # "Unhealthy"
        dietary_moderate = 0
        dietary_unhealthy = 1

    # Create DataFrame for prediction with the required feature order
    input_dict = {
        "Age": [age],
        "Work_Pressure": [work_pressure],
        "Job_Satisfaction": [job_satisfaction],
        "Sleep_Duration": [sleep_duration],
        "Work_or_Study_Hours": [work_or_study_hours],
        "Financial_Stress": [financial_stress],
        "Gender_Male": [gender_male],
        "Working_Professional_or_Student_Working_Professional": [working_professional_val],
        "Have_you_ever_had_suicidal_thoughts_?_Yes": [suicidal_thoughts_val],
        "Dietary_Habits_Moderate": [dietary_moderate],
        "Dietary_Habits_Unhealthy": [dietary_unhealthy],
        "Family_History_of_Mental_Illness_Yes": [family_history_val]
    }
    input_df = pd.DataFrame(input_dict)
    
    # Scale the input data
    scaled_input = scaler.transform(input_df)
    
    # Get prediction from the Keras model (probability)
    pred_prob = keras_model.predict(scaled_input)
    pred = (pred_prob > 0.65).astype("int32").flatten()[0]
    
    # Determine the prediction result and motivational message
    if pred == 1:
        result_text = "Depressed"
        result_color = "#e74c3c"  # red
        motivation = ("It seems you might be going through a tough time. "
                      "Remember, you are not alone and help is available. "
                      "Consider reaching out to a trusted friend or professional. "
                      "Taking the first step can make a big difference!")
    else:
        result_text = "Not Depressed"
        result_color = "#27ae60"  # green
        motivation = ("Great job! It looks like you're in a positive state. "
                      "Keep taking care of your mental health, maintain a balanced lifestyle, "
                      "and continue to nurture what makes you happy. Stay positive!")
    
    # Display the prediction result with a custom HTML block for decoration
    st.subheader("Prediction Result")
    st.markdown(f"""
    <div style='padding: 20px; background-color: #f9f9f9; border-radius: 10px; text-align: center;'>
        <h2 style='color: {result_color};'>The model predicts: {result_text}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the motivational message
    st.markdown(f"""
    <div style='padding: 15px; background-color: #f0f0f0; border-radius: 10px; margin-top: 20px;'>
        <p style='font-size: 16px; color: #333;'>
            {motivation}
        </p>
    </div>
    """, unsafe_allow_html=True)
