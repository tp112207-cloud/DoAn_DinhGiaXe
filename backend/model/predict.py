import joblib
import numpy as np
import os
import json

# Tỷ giá chuyển đổi INR sang VND (1 INR ≈ 300 VND)
INR_TO_VND = 300

class CarPricePredictor:
    def __init__(self):
        model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model = joblib.load(os.path.join(model_dir, 'car_price_model.pkl'))
        self.label_encoders = joblib.load(os.path.join(model_dir, 'label_encoders.pkl'))
        
        with open(os.path.join(model_dir, 'model_metadata.json'), 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
    
    def predict(self, name, year, km_driven, fuel, transmission, owner,
                mileage=None, engine=None, max_power=None, seats=5):
        """Predict car price"""
        try:
            # Extract brand
            brand = name.split(' ')[0] if name else 'Maruti'
            if name and name.startswith('Mercedes'):
                brand = 'Mercedes-Benz'
            elif name and name.startswith('Land Rover'):
                brand = 'Land Rover'
            
            # Encode categorical
            encoded = {}
            inputs = {
                'fuel': fuel,
                'seller_type': 'Individual',
                'transmission': transmission,
                'owner': owner,
                'brand': brand,
            }
            
            for col, value in inputs.items():
                le = self.label_encoders[col]
                if value in le.classes_:
                    encoded[col] = le.transform([value])[0]
                else:
                    encoded[col] = 0
            
            # Build features (same order as training)
            features = np.array([[
                encoded['fuel'],
                encoded['seller_type'],
                encoded['transmission'],
                encoded['owner'],
                encoded['brand'],
                int(year),
                int(km_driven),
                float(mileage) if mileage else 17.0,
                float(engine) if engine else 1200.0,
                float(max_power) if max_power else 80.0,
                float(seats),
            ]])
            
            predicted = self.model.predict(features)[0]
            predicted = max(0, predicted)
            
            # Confidence interval from estimators
            predictions = []
            for est in self.model.estimators_[:50]:
                p = est[0].predict(features)[0]
                predictions.append(p)
            
            std_dev = np.std(predictions) if predictions else predicted * 0.1
            confidence_low = max(0, predicted - 1.5 * std_dev)
            confidence_high = predicted + 1.5 * std_dev
            
            # Chuyển đổi từ INR sang VND
            predicted_vnd = predicted * INR_TO_VND
            confidence_low_vnd = max(0, predicted - 1.5 * std_dev) * INR_TO_VND
            confidence_high_vnd = (predicted + 1.5 * std_dev) * INR_TO_VND
            
            return {
                'predicted_price': round(float(predicted_vnd), 0),
                'confidence_low': round(float(confidence_low_vnd), 0),
                'confidence_high': round(float(confidence_high_vnd), 0),
                'confidence_percent': round(float(self.metadata['r2_score'] * 100), 1),
                'currency': 'VND',
            }
        except Exception as e:
            return {'error': str(e), 'predicted_price': None}
    
    def get_brands(self):
        return sorted(self.label_encoders['brand'].classes_.tolist())
    
    def get_fuel_types(self):
        return sorted(self.label_encoders['fuel'].classes_.tolist())
    
    def get_transmission_types(self):
        return sorted(self.label_encoders['transmission'].classes_.tolist())
    
    def get_owner_types(self):
        return sorted(self.label_encoders['owner'].classes_.tolist())
