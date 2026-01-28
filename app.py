from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
from flask_cors import CORS
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
CORS(app)

try:
    model = joblib.load('models/model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    gender_encoder = joblib.load('models/gender_encoder.pkl')
    diagnosis_encoder = joblib.load('models/diagnosis_encoder.pkl')
    feature_dict = joblib.load('models/feature_dict.pkl')
    all_features = feature_dict['all_features']
    
    print("All models loaded successfully")
    print(f"Model features: {all_features}")
    
except Exception as e:
    print(f"Error loading models: {e}")
    raise

symptom_info = {
    'fever': {'name': 'Fever', 'min': 0, 'max': 3, 'description': 'Body temperature abnormality'},
    'cough': {'name': 'Cough', 'min': 0, 'max': 3, 'description': 'Cough severity'},
    'fatigue': {'name': 'Fatigue', 'min': 0, 'max': 3, 'description': 'Tiredness level'},
    'headache': {'name': 'Headache', 'min': 0, 'max': 3, 'description': 'Head pain intensity'},
    'muscle_pain': {'name': 'Muscle Pain', 'min': 0, 'max': 3, 'description': 'Muscle ache severity'},
    'nausea': {'name': 'Nausea', 'min': 0, 'max': 3, 'description': 'Feeling sick'},
    'vomiting': {'name': 'Vomiting', 'min': 0, 'max': 3, 'description': 'Vomiting frequency'},
    'diarrhea': {'name': 'Diarrhea', 'min': 0, 'max': 3, 'description': 'Diarrhea severity'},
    'skin_rash': {'name': 'Skin Rash', 'min': 0, 'max': 3, 'description': 'Skin condition'},
    'loss_smell': {'name': 'Loss of Smell', 'min': 0, 'max': 3, 'description': 'Smell impairment'},
    'loss_taste': {'name': 'Loss of Taste', 'min': 0, 'max': 3, 'description': 'Taste impairment'},
}

vital_info = {
    'age': {'name': 'Age', 'min': 0, 'max': 100, 'description': 'Patient age'},
    'gender': {'name': 'Gender', 'options': ['Male', 'Female'], 'description': 'Patient gender'},
    'systolic_bp': {'name': 'Systolic BP', 'min': 80, 'max': 200, 'description': 'Upper blood pressure'},
    'diastolic_bp': {'name': 'Diastolic BP', 'min': 40, 'max': 120, 'description': 'Lower blood pressure'},
    'heart_rate': {'name': 'Heart Rate', 'min': 40, 'max': 150, 'description': 'Beats per minute'},
    'temperature_c': {'name': 'Temperature', 'min': 34, 'max': 42, 'description': 'Body temperature (°C)'},
    'oxygen_saturation': {'name': 'Oxygen Saturation', 'min': 85, 'max': 100, 'description': 'Blood oxygen level'},
}

lab_info = {
    'wbc_count': {'name': 'WBC Count', 'min': 2, 'max': 15, 'description': 'White blood cells'},
    'hemoglobin': {'name': 'Hemoglobin', 'min': 8, 'max': 18, 'description': 'Blood protein level'},
    'platelet_count': {'name': 'Platelet Count', 'min': 50, 'max': 500, 'description': 'Platelets in blood'},
    'crp_level': {'name': 'CRP Level', 'min': 0, 'max': 30, 'description': 'Inflammation marker'},
    'glucose_level': {'name': 'Glucose Level', 'min': 50, 'max': 200, 'description': 'Blood sugar level'},
}

disease_info = {
    'COVID-19': {'description': 'Coronavirus disease'},
    'Dengue': {'description': 'Mosquito-borne viral infection'},
    'Influenza': {'description': 'Seasonal flu virus'},
    'Malaria': {'description': 'Parasitic disease from mosquitoes'},
    'Pneumonia': {'description': 'Lung inflammation infection'},
}

@app.route('/')
def home():
    return render_template('index.html', 
                         symptom_info=symptom_info,
                         vital_info=vital_info,
                         lab_info=lab_info,
                         disease_info=disease_info)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        input_data = []
        gender_encoded = gender_encoder.transform([data['gender']])[0]
        
        for feature in all_features:
            if feature == 'gender_encoded':
                input_data.append(gender_encoded)
            elif feature in data:
                input_data.append(float(data[feature]))
            else:
                input_data.append(0)
        
        input_array = np.array(input_data).reshape(1, -1)
        input_scaled = scaler.transform(input_array)
        prediction_encoded = model.predict(input_scaled)[0]
        prediction_prob = model.predict_proba(input_scaled)[0]
        diagnosis = diagnosis_encoder.inverse_transform([prediction_encoded])[0]
        
        probabilities = {}
        for i, disease in enumerate(diagnosis_encoder.classes_):
            probabilities[disease] = float(prediction_prob[i]) * 100
        
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        
        disease_data = disease_info.get(diagnosis, {'description': 'Unknown disease'})
        
        response = {
            'success': True,
            'diagnosis': diagnosis,
            'description': disease_data['description'],
            'confidence': round(probabilities[diagnosis], 2),
            'all_probabilities': [
                {'disease': disease, 'probability': round(prob, 2)}
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
    return jsonify({
        'symptoms': symptom_info,
        'vitals': vital_info,
        'lab_tests': lab_info
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Medical Diagnosis Prediction System")
    print("="*50)
    print("Starting server...")
    print("Open browser: http://127.0.0.1:5000")
    print("="*50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)