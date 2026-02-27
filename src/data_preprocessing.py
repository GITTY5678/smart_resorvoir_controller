import pandas as pd
import numpy as np
import os

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

RAW_DATA_PATH = "data/raw/reservoir_data.csv"
PROCESSED_DATA_PATH = "data/processed/clean_reservoir_data.csv"

# --------------------------------------------------
# STEP 1: LOAD DATA
# --------------------------------------------------

def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
    
    df = pd.read_csv(filepath)
    print("Raw Data Loaded Successfully.")
    print(df.head())
    return df


# --------------------------------------------------
# STEP 2: BASIC CLEANING
# --------------------------------------------------

def clean_data(df):
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Expected columns
    required_columns = ["date", "inflow", "rainfall", "storage", "release"]
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Convert date
    df["date"] = pd.to_datetime(df["date"])
    
    # Sort by date
    df = df.sort_values("date")
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(method="ffill")
    
    # Remove unrealistic values
    df = df[df["storage"] >= 0]
    df = df[df["inflow"] >= 0]
    df = df[df["release"] >= 0]
    
    print("Data Cleaning Completed.")
    return df


# --------------------------------------------------
# STEP 3: FEATURE ENGINEERING
# --------------------------------------------------

def feature_engineering(df):
    
    # Create next day storage target
    df["next_day_storage"] = df["storage"].shift(-1)
    
    # Drop last row (since it has NaN target)
    df = df.dropna()
    
    print("Feature Engineering Completed.")
    return df


# --------------------------------------------------
# STEP 4: SAVE PROCESSED DATA
# --------------------------------------------------

def save_data(df, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Processed Data Saved to {filepath}")


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def run_pipeline():
    
    df = load_data(RAW_DATA_PATH)
    df = clean_data(df)
    df = feature_engineering(df)
    save_data(df, PROCESSED_DATA_PATH)
    
    print("Phase 1 Data Pipeline Completed Successfully.")


if __name__ == "__main__":
    run_pipeline()
