import pandas as pd
import numpy as np
import os
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

PROCESSED_DATA_PATH = "data/processed/clean_reservoir_data.csv"
MODEL_SAVE_PATH = "models/reservoir_model.pkl"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_processed_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError("Processed dataset not found. Run Phase 1 first.")
    
    df = pd.read_csv(filepath)
    print("Processed dataset loaded successfully.")
    return df


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

def train_model(df):
    
    # Features and target
    X = df[["inflow", "rainfall", "storage", "release"]]
    y = df["next_day_storage"]
    
    # Time-series split (no shuffle)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    
    # Metrics
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print("\n--- MODEL PERFORMANCE ---")
    print(f"MAE  : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"R2   : {r2:.3f}")
    
    return model, mae, rmse, r2


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

def save_model(model, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model saved at {filepath}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def run_training_pipeline():
    
    df = load_processed_data(PROCESSED_DATA_PATH)
    
    model, mae, rmse, r2 = train_model(df)
    
    save_model(model, MODEL_SAVE_PATH)
    
    print("\nPhase 2 Completed Successfully.")


if __name__ == "__main__":
    run_training_pipeline()