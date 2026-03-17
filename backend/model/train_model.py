import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import json

def train_model():
    """Train car price prediction model using cardekho.csv dataset"""
    # Try loading from SQL Server first, fallback to CSV
    model_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(model_dir, '..', 'data', 'cardekho.csv')
    
    try:
        from database import get_all_cars
        df = get_all_cars()
        print(f'Loaded {len(df)} records from SQL Server')
    except Exception:
        df = pd.read_csv(data_path)
        df = df.rename(columns={'mileage(km/ltr/kg)': 'mileage'})
        print(f'Loaded {len(df)} records from CSV')
    
    # Extract brand from name
    def extract_brand(name):
        name = str(name)
        if name.startswith('Mercedes'):
            return 'Mercedes-Benz'
        if name.startswith('Land Rover'):
            return 'Land Rover'
        return name.split(' ')[0]
    
    df['brand'] = df['name'].apply(extract_brand)
    
    # Clean max_power - convert to numeric
    df['max_power_num'] = pd.to_numeric(
        df['max_power'].astype(str).str.replace(' bhp', '').str.strip(),
        errors='coerce'
    )
    
    # Drop rows with missing key values
    df = df.dropna(subset=['mileage', 'engine', 'max_power_num', 'seats'])
    df = df[df['selling_price'] > 0]
    
    print(f'After cleaning: {len(df)} records')
    print(f'Brands: {df["brand"].nunique()}')
    print(f'Price range: {df["selling_price"].min():,} - {df["selling_price"].max():,}')
    
    # Features
    categorical_cols = ['fuel', 'seller_type', 'transmission', 'owner', 'brand']
    numerical_cols = ['year', 'km_driven', 'mileage', 'engine', 'max_power_num', 'seats']
    
    # Label encode
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
    
    feature_cols = [c + '_encoded' for c in categorical_cols] + numerical_cols
    
    X = df[feature_cols]
    y = df['selling_price']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f'\n--- Model Performance ---')
    print(f'MAE: {mae:,.0f}')
    print(f'R2 Score: {r2:.4f}')
    print(f'Accuracy: {r2*100:.1f}%')
    
    # Feature importance
    feat_names = categorical_cols + numerical_cols
    importance = dict(zip(feat_names, model.feature_importances_))
    print(f'\n--- Feature Importance ---')
    for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f'  {feat}: {imp:.4f}')
    
    # Save model
    joblib.dump(model, os.path.join(model_dir, 'car_price_model.pkl'))
    joblib.dump(label_encoders, os.path.join(model_dir, 'label_encoders.pkl'))
    
    # Save metadata
    metadata = {
        'feature_cols': feature_cols,
        'categorical_cols': categorical_cols,
        'numerical_cols': numerical_cols,
        'mae': float(mae),
        'r2_score': float(r2),
        'n_samples': len(df),
        'brands': sorted(df['brand'].unique().tolist()),
        'fuel_types': sorted(df['fuel'].unique().tolist()),
        'transmission_types': sorted(df['transmission'].unique().tolist()),
        'owner_types': sorted(df['owner'].unique().tolist()),
        'year_range': [int(df['year'].min()), int(df['year'].max())],
        'feature_importance': {k: float(v) for k, v in importance.items()}
    }
    
    with open(os.path.join(model_dir, 'model_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f'\nModel saved to {model_dir}')
    return model, label_encoders, metadata

if __name__ == '__main__':
    train_model()
