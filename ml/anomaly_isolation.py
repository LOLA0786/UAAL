"""
IsolationForest anomaly detector wrapper for UAAL.
This includes a simple fit / detect API. In production use incremental models or streaming infra.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_PATH = os.environ.get("UAAL_MODEL_PATH", "ml/isolation.pkl")

def train(values):
    X = np.array(values).reshape(-1, 1)
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    return True

def detect(value):
    if not os.path.exists(MODEL_PATH):
        # not trained, return False
        return False
    model = joblib.load(MODEL_PATH)
    v = np.array([[value]])
    pred = model.predict(v)
    # -1 is anomaly
    return pred[0] == -1
