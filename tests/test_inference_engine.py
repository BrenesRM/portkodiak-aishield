import sys
import os
import unittest

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.inference_engine import InferenceEngine

class TestInferenceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = InferenceEngine()
        
    def test_model_loading(self):
        # We expect a model to be present since we trained it
        if os.path.exists(self.engine.model_path):
            self.assertIsNotNone(self.engine.model, "Model should be loaded")
        else:
            self.assertIsNone(self.engine.model, "Model should be None if file missing")

    def test_prediction(self):
        # Mock connection info
        conn = {
            "remote_port": 443,
            "process_name": "chrome.exe",
            "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "direction": "Outbound"
        }
        
        score, label = self.engine.predict(conn)
        print(f"Prediction: {label} ({score})")
        
        self.assertIsInstance(score, float)
        self.assertIn(label, ["Normal", "Anomaly", "Unknown (No Model)", "Error"])

if __name__ == "__main__":
    unittest.main()
