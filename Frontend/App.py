import streamlit as st
import requests
import os  # <-- Yeh line missing thi, isay lazmi add karein!

# 1. Aapki GitHub Repository ka direct RAW image link
github_logo_url = "https://raw.githubusercontent.com/khurramks1111-vibe/Crop-Yield-Predictor/master/Frontend/logo.png"

# 2. Page Configuration
st.set_page_config(
    page_title="Crop Yield Predictor",
    page_icon=github_logo_url,
    layout="centered"
)

# 3. Beautiful Custom CSS Hero Banner
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1e5128 0%, #4e9f3d 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    ">
        <h1 style="color: white; font-family: 'Segoe UI', sans-serif; margin: 0; font-size: 2.3rem;">
            🌾 Crop Yield Prediction Dashboard
        </h1>
        <p style="color: #d8f3dc; font-family: 'Segoe UI', sans-serif; margin-top: 10px; font-size: 1.1rem; opacity: 0.9; margin-bottom: 0;">
            FastAPI backend se connected machine learning prediction system (Python 3.14)
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Yahan se aage aap ka baaki prediction ka code (inputs, buttons, etc.) shuru hoga...

# 5. Titles & Headers

# FastAPI Backend URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000") + "/predict"

# 1. Inputs Form
with st.form("prediction_form"):
    st.subheader("📋 Input Farm & Weather Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        country = st.selectbox("Country", ["India", "USA", "Brazil", "Australia", "Canada"])
        region = st.text_input("Region / State", "Punjab")
        crop_type = st.selectbox("Crop Type", ["Wheat", "Rice", "Maize", "Soybeans", "Cotton"])
        temp = st.slider("Average Temperature (°C)", 10.0, 45.0, 25.0, step=0.1)
        precip = st.slider("Total Precipitation (mm)", 50.0, 1500.0, 500.0, step=10.0)
        co2 = st.number_input("CO2 Emissions (MT)", min_value=0.0, value=12.5, step=0.1)
        
    with col2:
        extreme_events = st.slider("Extreme Weather Events (Days)", 0, 30, 2)
        irrigation = st.slider("Irrigation Access (%)", 0.0, 100.0, 80.0, step=1.0)
        pesticide = st.number_input("Pesticide Use (KG per HA)", min_value=0.0, value=3.2, step=0.1)
        fertilizer = st.number_input("Fertilizer Use (KG per HA)", min_value=0.0, value=150.0, step=1.0)
        soil_health = st.slider("Soil Health Index", 0.0, 100.0, 75.0, step=1.0)
        adaptation = st.selectbox("Adaptation Strategies", [
            "No Adaptation", 
            "Water Management", 
            "Crop Rotation", 
            "Organic Farming", 
            "Drought-resistant Crops"
        ])

    # Submit Button
    submit_btn = st.form_submit_button("🔮 Predict Crop Yield")

# 2. Handle Prediction
if submit_btn:
    # Prepare payload according to FastAPI's PredictionInput schema
    payload = {
        "Country": country,
        "Region": region,
        "Crop_Type": crop_type,
        "Average_Temperature_C": float(temp),
        "Total_Precipitation_mm": float(precip),
        "CO2_Emissions_MT": float(co2),
        "Extreme_Weather_Events": int(extreme_events),
        "Irrigation_Access_percent": float(irrigation),
        "Pesticide_Use_KG_per_HA": float(pesticide),
        "Fertilizer_Use_KG_per_HA": float(fertilizer),
        "Soil_Health_Index": float(soil_health),
        "Adaptation_Strategies": adaptation
    }
    
    with st.spinner("⏳prediction fetch from Backend API ..."):
        try:
            response = requests.post(BACKEND_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                predicted_yield = result.get("predicted_crop_yield", 0.0)
                
                # Display Results
                st.success("🎉 Prediction Successful!")
                st.metric(
                    label=f"Predicted Yield for {crop_type} ({country})", 
                    value=f"{predicted_yield:.4f} MT/HA"
                )
                
                # Friendly message based on yield quality
                if predicted_yield > 4.0:
                    st.balloons()
                    st.info("🌟 Outstanding Yield! Farm management practices and soil conditions are ideal.")
                elif predicted_yield > 2.0:
                    st.info("👍 Good Yield. Moderate adaptation strategies can further improve productivity.")
                else:
                    st.warning("⚠️ Low Yield Warning. Check Soil Health or apply adaptation strategies like 'Water Management'.")
            else:
                st.error(f"❌ Backend ne error return kiya: {response.status_code}")
                st.write(response.text)
        except requests.exceptions.ConnectionError:
            st.error("❌ FastAPI not connected toBackend (port 8000) ! Does your backend server run in background?")