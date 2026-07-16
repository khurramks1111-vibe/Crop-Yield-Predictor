 # train.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

print("🔄 Local environment ke mutabiq model training shuru ho rahi hai...")

csv_filename = 'climate_change_impact_on_agriculture_2024.csv'
if not os.path.exists(csv_filename):
    raise FileNotFoundError(f"❌ Error: '{csv_filename}' file Backend folder mein nahi mili!")

df = pd.read_csv(csv_filename)

# 1. Target Alignment (Agronomic rules)
np.random.seed(42)
soil_factor = (df['Soil_Health_Index'] - 30) / 70.0
irrigation_factor = (df['Irrigation_Access_%'] - 10) / 90.0
input_factor = (df['Fertilizer_Use_KG_per_HA'] + df['Pesticide_Use_KG_per_HA']) / 150.0

temp_stress = np.exp(-((df['Average_Temperature_C'] - 20) ** 2) / (2 * (10 ** 2)))

adaptation_map = {
    'No Adaptation': 1.0,
    'Water Management': 0.5,
    'Crop Rotation': 0.6,
    'Organic Farming': 0.7,
    'Drought-resistant Crops': 0.4
}
adaptation_mitigation = df['Adaptation_Strategies'].map(adaptation_map)
weather_penalty = (df['Extreme_Weather_Events'] / 10.0) * 0.4 * adaptation_mitigation

base_yield = 1.0 + (1.5 * soil_factor) + (1.2 * irrigation_factor) + (0.8 * input_factor)
realistic_yield = base_yield * temp_stress * (1.0 - weather_penalty)

noise = np.random.normal(0, 0.05, size=len(df))
df['Crop_Yield_MT_per_HA'] = np.clip(realistic_yield + noise, 0.5, 6.0)

# 2. Features aur Target split
X = df.drop(columns=['Crop_Yield_MT_per_HA', 'Economic_Impact_Million_USD', 'Year'])
y = df['Crop_Yield_MT_per_HA']

# Categorical aur Numerical columns setup
categorical_cols = ['Country', 'Region', 'Crop_Type', 'Adaptation_Strategies']
numerical_cols = [col for col in X.columns if col not in categorical_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# Pipeline assembly
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
])

# Train model
model_pipeline.fit(X, y)

# 3. Model save karein locally (Python 3.14 + sklearn 1.9.0 compatible)
model_name = 'crop_yield_local_model.pkl'
joblib.dump(model_pipeline, model_name)

print(f"✅ Behtareen! Naya model locally train ho kar '{model_name}' ke naam se save ho chuka hai.")