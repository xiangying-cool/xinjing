# Predicting Depression from Mental Health Survey Data with Deep Learning

This project utilizes a neural network model to predict whether an individual is experiencing depression based on various personal, lifestyle, and work-related features. The pipeline includes data preprocessing, model training (handling class imbalance), evaluation, and a user-friendly **Streamlit web application** for real-time predictions.

## Table of Contents  
- [Overview](#overview)  
- [Jupyter Notebook](#jupyter-notebook)  
- [Dataset](#dataset)  
- [Features](#features)  
- [Model Architecture](#model-architecture)  
- [Project Structure](#project-structure)  
- [Installation](#installation)  
- [Usage](#usage)  
  - [Training and Evaluation](#training-and-evaluation)  
  - [Running the Streamlit App](#running-the-streamlit-app)  
- [Evaluation Metrics](#evaluation-metrics)  
- [Live Demo](#live-demo)  

---

## Overview  

This project builds a **binary classification model** to predict depression status using a **deep learning-based pipeline**. The key components include:

- **Data Exploration & Preprocessing:** Conducted in a Jupyter Notebook (`health.ipynb`).
- **Neural Network Training:** A TensorFlow/Keras-based model trained with computed class weights to handle **class imbalance**.
- **Model Evaluation:** Performance metrics such as **accuracy, precision, recall, F1-score**, and fairness evaluation across demographic groups.
- **Deployment:** A **Streamlit app** allowing users to enter their details and receive predictions with **motivational messages** based on the result.

---

## Jupyter Notebook  

The **`health.ipynb`** notebook contains the following steps:  
- Data Cleaning & Exploration  
- Handling Class Imbalance  
- Feature Engineering & Encoding  
- Neural Network Training using **TensorFlow/Keras**  
- Model Evaluation with **classification metrics**  
- Saving the trained **model & scaler** for deployment  

---

## Dataset  

The dataset contains multiple features related to **age, work pressure, sleep duration, job satisfaction, financial stress**, and **mental health history**. The **target variable** is:  
- `Depression`: **1 (Depressed), 0 (Not Depressed)**  

class weights are used to improve model performance.

---

## Features  

| Feature Name | Description |
|-------------|-------------|
| `Age` | Age of the individual |
| `Work_Pressure` | Stress level at work (0-5 scale) |
| `Job_Satisfaction` | Satisfaction with job (0-5 scale) |
| `Sleep_Duration` | Average sleep hours per day |
| `Work_or_Study_Hours` | Daily work/study hours |
| `Financial_Stress` | Financial burden level (0-5 scale) |
| `Gender_Male` | 1 if Male, 0 if Female |
| `Working_Professional_or_Student_Working_Professional` | 1 if working professional, 0 if student |
| `Have_you_ever_had_suicidal_thoughts_?_Yes` | 1 if Yes, 0 if No |
| `Dietary_Habits_Moderate` | 1 if dietary habits are moderate, 0 otherwise |
| `Dietary_Habits_Unhealthy` | 1 if dietary habits are unhealthy, 0 otherwise |
| `Family_History_of_Mental_Illness_Yes` | 1 if Yes, 0 if No |

---

## Model Architecture  

The model is a **feedforward neural network** with the following layers:
- **Input Layer:** Accepts all feature inputs.
- **Hidden Layers:**  
  - **Dense Layer (32 neurons, ReLU activation) + Dropout (0.2)**
  - **Dense Layer (16 neurons, ReLU activation)**
- **Output Layer:**  
  - **1 neuron (Sigmoid activation)** for binary classification.

**Optimizer:** Adam | **Loss Function:** Binary Crossentropy

---
## Evaluation Metrics

- **Validation Accuracy:** 0.9277

**Classification Report-1(health.ipynb):**

```
               precision    recall  f1-score   support

           0       0.97      0.94      0.96     22986
           1       0.77      0.86      0.81      5154

    accuracy                           0.93     28140
   macro avg       0.87      0.90      0.88     28140
weighted avg       0.93      0.93      0.93     28140
```

- **Validation Accuracy:** 0.9373
  
**Classification Report-2(pipeline.ipynb):**
```
                 precision    recall  f1-score   support

           0       0.95      0.92      0.94     22873
           1       0.92      0.95      0.94     23152

    accuracy                           0.94     46025
   macro avg       0.94      0.94      0.94     46025
weighted avg       0.94      0.94      0.94     46025
```
## Streamlit Application

The Streamlit app offers a simple interface for real-time depression prediction. Users enter their personal details, and the app uses a pre-saved scaler and trained neural network (`keras_model.h5`) to output a prediction ("Depressed" or "Not Depressed") along with a tailored motivational message.

### Running the App

1. Ensure `keras_model.h5` and `scaler.pkl` are in the project directory.
2. Run the app:
   ```bash
   streamlit run streamlit_app.py
   
### Live Demo

Try the app live: 👉 [Streamlit Live App](https://svhhfumqygrpz2pahyxtlw.streamlit.app/)

© 2025 MuraliKrishnaGR. All rights reserved
