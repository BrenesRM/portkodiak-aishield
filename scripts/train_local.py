import pandas as pd
import numpy as np
import joblib
import glob
import os
import sys
from sklearn.ensemble import IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.feature_extraction.text import HashingVectorizer

# Ensure ml/models dir exists
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_latest_export():
    """Finds the latest traffic_export csv."""
    pattern = os.path.join(os.path.dirname(__file__), '..', 'traffic_export_*.csv')
    files = glob.glob(pattern)
    if not files:
        print("No traffic_export csv found!")
        return None
    latest_file = max(files, key=os.path.getctime)
    print(f"Loading data from {latest_file}...")
    return pd.read_csv(latest_file)

from sklearn.base import BaseEstimator, TransformerMixin

# Custom Transformer for Hashing
class HashingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, n_features=32):
        self.n_features = n_features
        self.vec = None
        
    def fit(self, X, y=None):
        # Stateless
        self.vec = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm=None)
        return self
        
    def transform(self, X):
        if self.vec is None:
            self.vec = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm=None)
            
        if isinstance(X, pd.DataFrame):
            X = X.iloc[:, 0]
        # Handle nan/non-string
        X = X.fillna("Unknown").astype(str)
        return self.vec.transform(X).toarray()

def train_model():
    df = load_latest_export()
    if df is None:
        return
    
    if len(df) < 5:
        print("WARNING: Not enough data points to train meaningfully (need > 5).")
        # Proceed anyway for POC but result will be junk
    
    print(f"Training on {len(df)} samples...")

    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('port', StandardScaler(), ['remote_port']),
            ('proc', HashingTransformer(n_features=16), ['process_name']),
            ('path', HashingTransformer(n_features=32), ['process_path']),
            # 'direction' is categorical strings 'Inbound'/'Outbound'
            ('dir', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['direction']) 
        ],
        remainder='drop'
    )

    # Model
    # contamination=0.01 implies we expect ~1% anomalies in training data
    clf = IsolationForest(
        n_estimators=100, 
        contamination=0.01, 
        random_state=42, 
        n_jobs=-1
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', clf)
    ])

    try:
        pipeline.fit(df)
        print("Training successful.")
        
        # Save
        model_path = os.path.join(MODEL_DIR, 'portkodiak_model.pkl')
        joblib.dump(pipeline, model_path)
        print(f"Model saved to: {model_path}")
        
    except Exception as e:
        print(f"Training failed: {e}")

if __name__ == "__main__":
    train_model()
