import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# 1. Load Data
print("="*50)
print("1. LOADING DATASET")
print("="*50)

try:
    df = pd.read_csv('medical_symptoms_dataset.csv')
    print(f"Dataset Shape: {df.shape}")
    print(f"\nTarget distribution:")
    print(df['diagnosis'].value_counts())
except FileNotFoundError:
    print("ERROR: 'medical_symptoms_dataset.csv' not found!")
    print("Please make sure the CSV file is in the same directory as this script.")
    exit(1)

# 2. Data Preprocessing
print("\n" + "="*50)
print("2. DATA PREPROCESSING")
print("="*50)

# Encode categorical variables
label_encoder = LabelEncoder()
df['gender_encoded'] = label_encoder.fit_transform(df['gender'])  # Male: 1, Female: 0

# Encode diagnosis for model
diagnosis_encoder = LabelEncoder()
df['diagnosis_encoded'] = diagnosis_encoder.fit_transform(df['diagnosis'])

# Prepare features
symptom_features = ['fever', 'cough', 'fatigue', 'headache', 'muscle_pain', 
                    'nausea', 'vomiting', 'diarrhea', 'skin_rash', 
                    'loss_smell', 'loss_taste']
vital_features = ['systolic_bp', 'diastolic_bp', 'heart_rate', 
                  'temperature_c', 'oxygen_saturation']
lab_features = ['wbc_count', 'hemoglobin', 'platelet_count', 
                'crp_level', 'glucose_level']

all_features = symptom_features + vital_features + lab_features + ['age', 'gender_encoded']

X = df[all_features]
y = df['diagnosis_encoded']

print(f"Number of features: {len(all_features)}")
print(f"Target classes: {diagnosis_encoder.classes_}")

# 3. Train-Test Split
print("\n" + "="*50)
print("3. TRAIN-TEST SPLIT")
print("="*50)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape}")
print(f"Testing set size: {X_test.shape}")

# 4. Feature Scaling
print("\n" + "="*50)
print("4. FEATURE SCALING")
print("="*50)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Scaling completed!")

# 5. Model Training
print("\n" + "="*50)
print("5. MODEL TRAINING")
print("="*50)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)

model.fit(X_train_scaled, y_train)

# 6. Model Evaluation
print("\n" + "="*50)
print("6. MODEL EVALUATION")
print("="*50)

y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"Training Accuracy: {train_accuracy:.4f}")
print(f"Testing Accuracy: {test_accuracy:.4f}")

print("\nClassification Report (Test Set):")
print(classification_report(y_test, y_test_pred, target_names=diagnosis_encoder.classes_))

# 7. Feature Importance
print("\n" + "="*50)
print("7. FEATURE IMPORTANCE")
print("="*50)

feature_importance = pd.DataFrame({
    'feature': all_features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 most important features:")
print(feature_importance.head(10))

# 8. Save Model and Encoders
print("\n" + "="*50)
print("8. SAVING MODEL AND ENCODERS")
print("="*50)

import os
if not os.path.exists('models'):
    os.makedirs('models')

# Save model
joblib.dump(model, 'models/model.pkl')
print("✓ Model saved as 'models/model.pkl'")

# Save scaler
joblib.dump(scaler, 'models/scaler.pkl')
print("✓ Scaler saved as 'models/scaler.pkl'")

# Save label encoders
joblib.dump(label_encoder, 'models/gender_encoder.pkl')
print("✓ Gender encoder saved as 'models/gender_encoder.pkl'")

joblib.dump(diagnosis_encoder, 'models/diagnosis_encoder.pkl')
print("✓ Diagnosis encoder saved as 'models/diagnosis_encoder.pkl'")

# Save feature list
feature_dict = {
    'symptoms': symptom_features,
    'vitals': vital_features,
    'lab_tests': lab_features,
    'all_features': all_features
}
joblib.dump(feature_dict, 'models/feature_dict.pkl')
print("✓ Feature dictionary saved as 'models/feature_dict.pkl'")

print("\n" + "="*50)
print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("="*50)
print("\nNext steps:")
print("1. Run: python app.py")
print("2. Open browser: http://localhost:5000")