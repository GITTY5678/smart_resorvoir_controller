import pandas as pd
import numpy as np
import joblib
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MODEL_PATH = "models/reservoir_model.pkl"
DATA_PATH = "data/processed/clean_reservoir_data.csv"

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def load_model(path):
    if not os.path.exists(path):
        raise FileNotFoundError("Model not found. Run Phase 2 first.")
    return joblib.load(path)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data(path):
    return pd.read_csv(path)


# --------------------------------------------------
# RELEASE OPTIMIZATION LOGIC
# --------------------------------------------------

def recommend_release(predicted_storage, current_release):
    
    ideal_target = 75
    
    if predicted_storage > 95:
        new_release = current_release * 1.5
    elif predicted_storage > 80:
        new_release = current_release * 1.2
    elif predicted_storage >= 60:
        new_release = current_release
    elif predicted_storage >= 40:
        new_release = current_release * 0.8
    else:
        new_release = current_release * 0.6
    
    return round(new_release, 2)


# --------------------------------------------------
# SIMULATE DECISION EFFECT
# --------------------------------------------------

def simulate_decision_effect(df, model):
    
    X = df[["inflow", "rainfall", "storage", "release"]]
    
    baseline_predictions = model.predict(X)
    
    optimized_predictions = []
    optimized_release_values = []
    
    for i in range(len(df)):
        row = df.iloc[i]
        predicted_storage = baseline_predictions[i]
        
        new_release = recommend_release(
            predicted_storage,
            row["release"]
        )
        
        # Simulate effect of new release
        adjusted_storage = (
            row["storage"]
            + (row["inflow"] / 1000)
            - (new_release / 1000)
            - 0.15
        )
        
        adjusted_storage = max(0, min(100, adjusted_storage))
        
        optimized_predictions.append(adjusted_storage)
        optimized_release_values.append(new_release)
    
    return baseline_predictions, optimized_predictions


# --------------------------------------------------
# EFFECTIVENESS SCORE
# --------------------------------------------------

def calculate_effectiveness(baseline, optimized):
    
    baseline_overflow = sum(1 for x in baseline if x > 95)
    optimized_overflow = sum(1 for x in optimized if x > 95)
    
    if baseline_overflow == 0:
        return 100
    
    reduction = ((baseline_overflow - optimized_overflow) / baseline_overflow) * 100
    
    return round(reduction, 2)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def run_optimization():
    
    model = load_model(MODEL_PATH)
    df = load_data(DATA_PATH)
    
    baseline, optimized = simulate_decision_effect(df, model)
    
    score = calculate_effectiveness(baseline, optimized)
    
    print("\n--- DECISION EFFECTIVENESS ---")
    print(f"Overflow Reduction Score: {score}%")
    
    print("\nPhase 3 Completed Successfully.")


if __name__ == "__main__":
    run_optimization()