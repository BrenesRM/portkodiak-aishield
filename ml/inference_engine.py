import os
import sys
import pandas as pd
import joblib
import logging

try:
    from ml.transformers import HashingTransformer
except ImportError:
    # Try adjusting path if running from agent
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from ml.transformers import HashingTransformer

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'portkodiak_model.pkl')
        
        self.model = None
        self.model_path = model_path
        self._load_model()
        
    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.warning(f"ML Model not found at {self.model_path}. Inference disabled.")
            return

        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Loaded ML model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")

    def predict(self, connection_info):
        """
        Predicts anomaly score for a connection.
        Returns: Score (float) and Label ("Normal"/"Anomaly")
        """
        if self.model is None:
            return 0.0, "Unknown (No Model)"
            
        try:
            # Prepare DataFrame for pipeline
            # Keys must match training columns
            # remote_port, process_name, process_path, direction
            
            data = {
                'remote_port': [connection_info.get('remote_port', 0)],
                'process_name': [connection_info.get('process_name', 'Unknown')],
                'process_path': [connection_info.get('process_path', 'Unknown')],
                'direction': [connection_info.get('direction', 'Outbound')]
            }
            
            df = pd.DataFrame(data)
            
            # Predict
            # score_samples: opposite of anomaly score. Lower is more anomalous. 
            # predict: -1 for outlier, 1 for inlier
            
            # Use predict first
            label_code = self.model.predict(df)[0]
            label = "Anomaly" if label_code == -1 else "Normal"
            
            # Get raw score
            score = self.model.decision_function(df)[0]
            
            return score, label
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.0, "Error"
