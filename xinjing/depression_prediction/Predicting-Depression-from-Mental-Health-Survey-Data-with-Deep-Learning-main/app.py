import streamlit as st
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from pipeline1 import (NullSatisfactionFiller, ColumnDropper, FormatCorrector,
                     NullDropper, SMOTENCTransformer, OutlierClipper,
                     OneHotEncoderWrapper, ColumnNameCleaner)

# Load the saved pipeline, scaler, and model
try:
    preprocessing_pipeline = joblib.load('preprocessing_pipeline.pkl')
    scaler = joblib.load('scaler.pkl')
    model = load_model('keras_model.h5')
except FileNotFoundError:
    st.error("Required files (preprocessing_pipeline.pkl, scaler.pkl, or keras_model.h5) not found.")
    st.stop()

# Streamlit App
st.title("Depression Prediction App")
st.markdown("Enter the details below to predict the likelihood of depression.")

# Input form
with st.form("input_form"):
    st.header("Input Features")

    # Numeric inputs
    age = st.number_input("Age", min_value=15, max_value=60, value=25)
    sleep_duration = st.selectbox("Sleep Duration (hours per night)", 
                                  ['Less than 5 hours', '1-2 hours', '2-3 hours', '3-4 hours', 
                                   '4-5 hours', '5-6 hours', '6-7 hours', '7-8 hours', 
                                   '8-9 hours', '9-11 hours', '10-11 hours', 'More than 8 hours'])
    work_study_hours = st.number_input("Work/Study Hours (per day)", min_value=0, max_value=12, value=8)
    financial_stress = st.slider("Financial Stress (1-5)", min_value=1, max_value=5, value=3)
    study_job_satisfaction = st.slider("Study/Job Satisfaction (1-5)", min_value=1, max_value=5, value=3)
    academic_work_pressure = st.slider("Academic/Work Pressure (1-5)", min_value=1, max_value=5, value=3)

    # Categorical inputs
    profession_status = st.selectbox("Working Professional or Student", ["Student", "Working Professional"])
    dietary_habits = st.selectbox("Dietary Habits", ["Healthy", "Moderate", "Unhealthy"])
    suicidal_thoughts = st.selectbox("Have you ever had suicidal thoughts?", ["No", "Yes"])
    family_history = st.selectbox("Family History of Mental Illness", ["No", "Yes"])

    # Additional fields for pipeline compatibility
    study_satisfaction = study_job_satisfaction
    job_satisfaction = study_job_satisfaction
    academic_pressure = academic_work_pressure
    work_pressure = academic_work_pressure

    submit_button = st.form_submit_button("Predict")

# Process input and make prediction
if submit_button:
    # Create input DataFrame
# Inside the `if submit_button:` block, modify input_data creation
    input_data = pd.DataFrame({
        'Age': [age],
        'Sleep Duration': [sleep_duration],
        'Work/Study Hours': [work_study_hours],
        'Financial Stress': [financial_stress],
        'Study/job Satisfaction': [study_job_satisfaction],
        'Academic/work Pressure': [academic_work_pressure],
        'Working Professional or Student': [profession_status],
        'Dietary Habits': [dietary_habits],
        'Have you ever had suicidal thoughts ?': [suicidal_thoughts],
        'Family History of Mental Illness': [family_history],
        'Study Satisfaction': [study_satisfaction],
        'Job Satisfaction': [job_satisfaction],
        'Academic Pressure': [academic_pressure],
        'Work Pressure': [work_pressure],
        # Add dummy columns expected by ColumnDropper
        'CGPA': [None],
        'Name': [''],
        'Gender': [''],
        'id': [None],
        'City': [''],
        'Profession': [''],
        'Degree': ['']
    })

    # Apply preprocessing to input data
    try:
        processed_data = preprocessing_pipeline.transform(input_data)
    except Exception as e:
        st.error(f"Error in preprocessing: {e}")
        st.stop()

    # Ensure all expected columns are present
    expected_columns = [
        'Age', 'Sleep_Duration', 'Work/Study_Hours', 'Financial_Stress',
        'Study/job_Satisfaction', 'Academic/work_Pressure',
        'Working_Professional_or_Student_Working_Professional',
        'Dietary_Habits_Moderate', 'Dietary_Habits_Unhealthy',
        'Have_you_ever_had_suicidal_thoughts_?_Yes',
        'Family_History_of_Mental_Illness_Yes'
    ]
    for col in expected_columns:
        if col not in processed_data.columns:
            processed_data[col] = 0
    processed_data = processed_data[expected_columns]

    # Apply scaling
    try:
        scaled_data = scaler.transform(processed_data)
    except Exception as e:
        st.error(f"Error in scaling: {e}")
        st.stop()

    # Make prediction
    try:
        prediction = model.predict(scaled_data, verbose=0)
        prediction = (prediction > 0.5).astype(int).flatten()[0]
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        st.stop()

    # Display results
    st.header("Prediction Result")
    if prediction == 1:
        st.error("The model predicts a **high likelihood of depression**. Please consult a healthcare professional.")
    else:
        st.success("The model predicts a **low likelihood of depression**. Keep monitoring your mental health.")
    
    # Display input data
    st.header("Input Data")
    st.write(input_data)