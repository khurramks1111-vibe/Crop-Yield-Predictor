 # Main.py
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os

app = FastAPI(title="Crop Yield Prediction API", version="1.2")

# Hamara local trained model jo 99% accuracy de raha hai
MODEL_PATH = 'crop_yield_local_model.pkl'

model = None

@app.on_event("startup")
def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model file '{MODEL_PATH}' nahi mili! Pehle train.py chalayein.")
        return
    
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully from local .pkl file on Python 3.14!")
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")

class PredictionInput(BaseModel):
    Country: str
    Region: str
    Crop_Type: str
    Average_Temperature_C: float
    Total_Precipitation_mm: float
    CO2_Emissions_MT: float
    Extreme_Weather_Events: int
    Irrigation_Access_percent: float
    Pesticide_Use_KG_per_HA: float
    Fertilizer_Use_KG_per_HA: float
    Soil_Health_Index: float
    Adaptation_Strategies: str

@app.get("/")
def home():
    status = "Loaded Successfully" if model is not None else "Not Loaded"
    return {"message": "Crop Yield Prediction API is active!", "model_status": status}

@app.post("/predict")
def predict_yield(data: PredictionInput):
    if model is None:
        return {"error": "Model is not loaded on the server."}
        
    input_df = pd.DataFrame([{
        'Country': data.Country,
        'Region': data.Region,
        'Crop_Type': data.Crop_Type,
        'Average_Temperature_C': data.Average_Temperature_C,
        'Total_Precipitation_mm': data.Total_Precipitation_mm,
        'CO2_Emissions_MT': data.CO2_Emissions_MT,
        'Extreme_Weather_Events': data.Extreme_Weather_Events,
        'Irrigation_Access_%': data.Irrigation_Access_percent,
        'Pesticide_Use_KG_per_HA': data.Pesticide_Use_KG_per_HA,
        'Fertilizer_Use_KG_per_HA': data.Fertilizer_Use_KG_per_HA,
        'Soil_Health_Index': data.Soil_Health_Index,
        'Adaptation_Strategies': data.Adaptation_Strategies
    }])
    
    prediction = model.predict(input_df)[0]
    return {"predicted_crop_yield": float(prediction)}