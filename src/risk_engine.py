import pandas as pd
import joblib
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MODEL_PATH = "models/reservoir_model.pkl"
DATA_PATH = "data/processed/clean_reservoir_data.csv"

# --------------------------------------------------
# LOAD
# --------------------------------------------------

def load_model(path):
    if not os.path.exists(path):
        raise FileNotFoundError("Model not found. Run Phase 2 first.")
    return joblib.load(path)

def load_data(path):
    return pd.read_csv(path)

# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------

def classify_risk(predicted_storage, rainfall):
    
    if predicted_storage > 95:
        return "FLOOD RISK"
    
    if predicted_storage < 25 and rainfall < 5:
        return "DROUGHT RISK"
    
    return "SAFE"

# --------------------------------------------------
# RUN RISK ANALYSIS
# --------------------------------------------------

def run_risk_detection():
    
    model = load_model(MODEL_PATH)
    df = load_data(DATA_PATH)
    
    X = df[["inflow", "rainfall", "storage", "release"]]
    
    predictions = model.predict(X)
    
    flood_count = 0
    drought_count = 0
    
    print("\n--- RISK ANALYSIS REPORT ---\n")
    
    for i in range(len(df)):
        risk = classify_risk(predictions[i], df.iloc[i]["rainfall"])
        
        if risk == "FLOOD RISK":
            flood_count += 1
        
        if risk == "DROUGHT RISK":
            drought_count += 1
        
        print(
            f"Day {i+1} | Predicted Storage: {predictions[i]:.2f}% | Risk: {risk}"
        )
    
    total_days = len(df)
    
    flood_percent = (flood_count / total_days) * 100
    drought_percent = (drought_count / total_days) * 100
    
    print("\n--- RISK SUMMARY ---")
    print(f"Flood Risk Days   : {flood_count} ({flood_percent:.2f}%)")
    print(f"Drought Risk Days : {drought_count} ({drought_percent:.2f}%)")
    
    print("\nPhase 4 Completed Successfully.")


if __name__ == "__main__":
    run_risk_detection()