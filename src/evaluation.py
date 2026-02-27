import pandas as pd
import numpy as np
import joblib
import os

from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MODEL_PATH = "models/reservoir_model.pkl"
DATA_PATH = "data/processed/clean_reservoir_data.csv"

# --------------------------------------------------
# LOAD
# --------------------------------------------------

def load_model(path):
    return joblib.load(path)

def load_data(path):
    return pd.read_csv(path)

# --------------------------------------------------
# FORECAST METRICS
# --------------------------------------------------

def forecast_accuracy(model, df):
    
    X = df[["inflow", "rainfall", "storage", "release"]]
    y_true = df["next_day_storage"]
    
    predictions = model.predict(X)
    
    mae = mean_absolute_error(y_true, predictions)
    r2 = r2_score(y_true, predictions)
    
    accuracy_percent = max(0, r2 * 100)
    
    return round(mae, 3), round(r2, 3), round(accuracy_percent, 2)

# --------------------------------------------------
# RISK DETECTION METRIC
# --------------------------------------------------

def risk_detection_accuracy(model, df):
    
    X = df[["inflow", "rainfall", "storage", "release"]]
    predictions = model.predict(X)
    
    actual_flood = df["next_day_storage"] > 95
    predicted_flood = predictions > 95
    
    correct = np.sum(actual_flood == predicted_flood)
    accuracy = (correct / len(df)) * 100
    
    return round(accuracy, 2)

# --------------------------------------------------
# DECISION EFFECTIVENESS
# --------------------------------------------------

def decision_effectiveness(model, df):
    
    X = df[["inflow", "rainfall", "storage", "release"]]
    baseline = model.predict(X)
    
    optimized = []
    
    for i in range(len(df)):
        row = df.iloc[i]
        predicted = baseline[i]
        
        if predicted > 95:
            new_release = row["release"] * 1.5
        else:
            new_release = row["release"]
        
        adjusted = (
            row["storage"]
            + (row["inflow"] / 1000)
            - (new_release / 1000)
            - 0.15
        )
        
        optimized.append(adjusted)
    
    baseline_overflow = sum(1 for x in baseline if x > 95)
    optimized_overflow = sum(1 for x in optimized if x > 95)
    
    if baseline_overflow == 0:
        return 100
    
    reduction = ((baseline_overflow - optimized_overflow) / baseline_overflow) * 100
    
    return round(reduction, 2)

# --------------------------------------------------
# RUN FULL EVALUATION
# --------------------------------------------------

def run_evaluation():
    
    model = load_model(MODEL_PATH)
    df = load_data(DATA_PATH)
    
    mae, r2, forecast_acc = forecast_accuracy(model, df)
    risk_acc = risk_detection_accuracy(model, df)
    decision_score = decision_effectiveness(model, df)
    
    print("\n--- FINAL SYSTEM METRICS ---\n")
    print(f"Forecast MAE              : {mae}")
    print(f"Forecast R2               : {r2}")
    print(f"Forecast Accuracy (%)     : {forecast_acc}%")
    print(f"Risk Detection Accuracy   : {risk_acc}%")
    print(f"Decision Effectiveness    : {decision_score}%")
    
    print("\nPhase 5 Completed Successfully.")


if __name__ == "__main__":
    run_evaluation()