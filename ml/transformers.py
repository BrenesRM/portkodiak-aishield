from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import HashingVectorizer
import pandas as pd

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
