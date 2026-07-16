 # evaluate.py
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import os

print("🔄 Model Evaluation shuru ho rahi hai...")

# 1. Load model and dataset
model_path = 'crop_yield_local_model.pkl'
csv_filename = 'climate_change_impact_on_agriculture_2024.csv'

if not os.path.exists(model_path) or not os.path.exists(csv_filename):
    print("❌ Error: Model file ya CSV file missing hai!")
    exit()

model = joblib.load(model_path)
df = pd.read_csv(csv_filename)

# 2. Target Alignment (Wahi formula jo training mein use hua)
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

# 3. Features and Target
X = df.drop(columns=['Crop_Yield_MT_per_HA', 'Economic_Impact_Million_USD', 'Year'])
y = df['Crop_Yield_MT_per_HA']

# 4. Split into Train and Test sets (Evaluation ke liye)
# Hum 20% data test set ke tor par nikalenge
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Make predictions on Test set
y_pred = model.predict(X_test)

# 6. Calculate Metrics
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n=== 📊 MODEL PERFORMANCE METRICS ===")
print(f"✅ R² (R-squared) Score : {r2:.4f}  ({r2*100:.2f}%)")
print(f"📉 Mean Absolute Error  : {mae:.4f} MT/HA")
print(f"📉 Root Mean Squared Error: {rmse:.4f} MT/HA")
print("=====================================\n")