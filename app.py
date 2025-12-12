from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
from flask_cors import CORS
import os

# Add this to prevent 403 errors
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
CORS(app)

# Load models and encoders
try:
    model = joblib.load('models/model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    gender_encoder = joblib.load('models/gender_encoder.pkl')
    diagnosis_encoder = joblib.load('models/diagnosis_encoder.pkl')
    feature_dict = joblib.load('models/feature_dict.pkl')
    all_features = feature_dict['all_features']
    
    print("✓ All models loaded successfully!")
    print(f"✓ Model features: {all_features}")
    print(f"✓ Diagnosis classes: {list(diagnosis_encoder.classes_)}")
    
except Exception as e:
    print(f"Error loading models: {e}")
    raise

# Symptom descriptions and emojis
symptom_info = {
    'fever': {'name': 'Fever', 'emoji': '🌡️', 'min': 0, 'max': 3, 'description': 'Body temperature abnormality'},
    'cough': {'name': 'Cough', 'emoji': '🤧', 'min': 0, 'max': 3, 'description': 'Cough severity'},
    'fatigue': {'name': 'Fatigue', 'emoji': '😴', 'min': 0, 'max': 3, 'description': 'Tiredness level'},
    'headache': {'name': 'Headache', 'emoji': '🤕', 'min': 0, 'max': 3, 'description': 'Head pain intensity'},
    'muscle_pain': {'name': 'Muscle Pain', 'emoji': '💪', 'min': 0, 'max': 3, 'description': 'Muscle ache severity'},
    'nausea': {'name': 'Nausea', 'emoji': '🤢', 'min': 0, 'max': 3, 'description': 'Feeling sick'},
    'vomiting': {'name': 'Vomiting', 'emoji': '🤮', 'min': 0, 'max': 3, 'description': 'Vomiting frequency'},
    'diarrhea': {'name': 'Diarrhea', 'emoji': '🚽', 'min': 0, 'max': 3, 'description': 'Diarrhea severity'},
    'skin_rash': {'name': 'Skin Rash', 'emoji': '🔴', 'min': 0, 'max': 3, 'description': 'Skin condition'},
    'loss_smell': {'name': 'Loss of Smell', 'emoji': '👃', 'min': 0, 'max': 3, 'description': 'Smell impairment'},
    'loss_taste': {'name': 'Loss of Taste', 'emoji': '👅', 'min': 0, 'max': 3, 'description': 'Taste impairment'},
}

# Vital signs info
vital_info = {
    'age': {'name': 'Age', 'emoji': '🎂', 'min': 0, 'max': 100, 'description': 'Patient age'},
    'gender': {'name': 'Gender', 'emoji': '👤', 'options': ['Male', 'Female'], 'description': 'Patient gender'},
    'systolic_bp': {'name': 'Systolic BP', 'emoji': '💓', 'min': 80, 'max': 200, 'description': 'Upper blood pressure'},
    'diastolic_bp': {'name': 'Diastolic BP', 'emoji': '💗', 'min': 40, 'max': 120, 'description': 'Lower blood pressure'},
    'heart_rate': {'name': 'Heart Rate', 'emoji': '❤️', 'min': 40, 'max': 150, 'description': 'Beats per minute'},
    'temperature_c': {'name': 'Temperature', 'emoji': '🌡️', 'min': 34, 'max': 42, 'description': 'Body temperature (°C)'},
    'oxygen_saturation': {'name': 'Oxygen Saturation', 'emoji': '🫁', 'min': 85, 'max': 100, 'description': 'Blood oxygen level'},
}

# Lab tests info
lab_info = {
    'wbc_count': {'name': 'WBC Count', 'emoji': '🔬', 'min': 2, 'max': 15, 'description': 'White blood cells'},
    'hemoglobin': {'name': 'Hemoglobin', 'emoji': '🩸', 'min': 8, 'max': 18, 'description': 'Blood protein level'},
    'platelet_count': {'name': 'Platelet Count', 'emoji': '🧫', 'min': 50, 'max': 500, 'description': 'Platelets in blood'},
    'crp_level': {'name': 'CRP Level', 'emoji': '📊', 'min': 0, 'max': 30, 'description': 'Inflammation marker'},
    'glucose_level': {'name': 'Glucose Level', 'emoji': '🍬', 'min': 50, 'max': 200, 'description': 'Blood sugar level'},
}

# Disease information with emojis and descriptions
disease_info = {
    'COVID-19': {'emoji': '🦠', 'color': '#FF6B6B', 'description': 'Coronavirus disease'},
    'Dengue': {'emoji': '🦟', 'color': '#FFA726', 'description': 'Mosquito-borne viral infection'},
    'Influenza': {'emoji': '🤒', 'color': '#42A5F5', 'description': 'Seasonal flu virus'},
    'Malaria': {'emoji': '🌡️', 'color': '#66BB6A', 'description': 'Parasitic disease from mosquitoes'},
    'Pneumonia': {'emoji': '🫁', 'color': '#AB47BC', 'description': 'Lung inflammation infection'},
}

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html', 
                         symptom_info=symptom_info,
                         vital_info=vital_info,
                         lab_info=lab_info,
                         disease_info=disease_info)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        # Get data from form
        data = request.json
        
        # Prepare input array
        input_data = []
        
        # Encode gender
        gender_encoded = gender_encoder.transform([data['gender']])[0]
        
        # Build feature vector in correct order
        for feature in all_features:
            if feature == 'gender_encoded':
                input_data.append(gender_encoded)
            elif feature in data:
                input_data.append(float(data[feature]))
            else:
                # For features not in request, use 0 (default)
                input_data.append(0)
        
        # Convert to numpy array and reshape
        input_array = np.array(input_data).reshape(1, -1)
        
        # Scale the input
        input_scaled = scaler.transform(input_array)
        
        # Make prediction
        prediction_encoded = model.predict(input_scaled)[0]
        prediction_prob = model.predict_proba(input_scaled)[0]
        
        # Decode prediction
        diagnosis = diagnosis_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get probabilities for all classes
        probabilities = {}
        for i, disease in enumerate(diagnosis_encoder.classes_):
            probabilities[disease] = float(prediction_prob[i]) * 100
        
        # Sort probabilities
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        
        # Get disease info
        disease_data = disease_info.get(diagnosis, {'emoji': '❓', 'color': '#9E9E9E', 'description': 'Unknown disease'})
        
        # Prepare response
        response = {
            'success': True,
            'diagnosis': diagnosis,
            'emoji': disease_data['emoji'],
            'color': disease_data['color'],
            'description': disease_data['description'],
            'confidence': round(probabilities[diagnosis], 2),
            'all_probabilities': [
                {'disease': disease, 'probability': round(prob, 2), 
                 'emoji': disease_info.get(disease, {}).get('emoji', '❓'),
                 'color': disease_info.get(disease, {}).get('color', '#9E9E9E')}
                for disease, prob in sorted_probs
            ],
            'severity': 'High' if probabilities[diagnosis] > 70 else 'Medium' if probabilities[diagnosis] > 40 else 'Low'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/feature_ranges', methods=['GET'])
def get_feature_ranges():
    """Get feature ranges for frontend validation"""
    return jsonify({
        'symptoms': symptom_info,
        'vitals': vital_info,
        'lab_tests': lab_info
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MEDICAL DIAGNOSIS PREDICTION SYSTEM")
    print("="*50)
    print("\nStarting server...")
    print("➡️ Open your browser and go to: http://127.0.0.1:5000")
    print("\n" + "="*50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)