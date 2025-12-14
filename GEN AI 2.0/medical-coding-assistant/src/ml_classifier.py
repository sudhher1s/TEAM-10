"""
ML Classifier - Neural Network for Direct Code Prediction
Trains on medical data to directly predict ICD-10 codes
"""
from __future__ import annotations
import numpy as np
from typing import Optional
from sklearn.preprocessing import MultiLabelBinarizer
import json
import os


class MLClassifier:
    """
    Neural network classifier for direct ICD-10 prediction
    Uses embedding features from semantic retriever
    """
    
    def __init__(self, embedding_dim: int = 384, max_codes: int = 100):
        """
        Initialize ML classifier
        
        Args:
            embedding_dim: Dimension of input embeddings
            max_codes: Maximum number of codes to predict
        """
        self.embedding_dim = embedding_dim
        self.max_codes = max_codes
        self.model = None
        self.mlb = MultiLabelBinarizer()
        self.is_fitted = False
        self.code_list = []
        self.config_path = "models/classifier_config.json"
        
        # Try to load keras/tensorflow
        try:
            import tensorflow as tf
            self.tf = tf
            print("✓ TensorFlow loaded")
        except ImportError:
            print("⚠ TensorFlow not available, using sklearn models")
            self.tf = None

    def _build_model(self) -> object:
        """Build neural network model"""
        if not self.tf:
            # Fallback to sklearn
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Build TensorFlow model
        model = self.tf.keras.Sequential([
            self.tf.keras.layers.Dense(256, activation='relu', input_dim=self.embedding_dim),
            self.tf.keras.layers.BatchNormalization(),
            self.tf.keras.layers.Dropout(0.3),
            
            self.tf.keras.layers.Dense(128, activation='relu'),
            self.tf.keras.layers.BatchNormalization(),
            self.tf.keras.layers.Dropout(0.2),
            
            self.tf.keras.layers.Dense(64, activation='relu'),
            self.tf.keras.layers.Dropout(0.1),
            
            self.tf.keras.layers.Dense(len(self.code_list), activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['hamming']
        )
        
        return model

    def fit(self, X: np.ndarray, y: list[list[str]]) -> None:
        """
        Train classifier on embeddings and ICD-10 codes
        
        Args:
            X: Embeddings array (n_samples, embedding_dim)
            y: List of code lists for each sample
        """
        print(f"Training ML Classifier on {len(X)} samples...")
        
        # Get unique codes
        self.code_list = sorted(set(code for codes in y for code in codes))[:self.max_codes]
        
        # Encode labels
        self.mlb.fit([self.code_list])
        y_encoded = self.mlb.transform(y)
        
        # Build and train model
        self.model = self._build_model()
        
        if self.tf and hasattr(self.model, 'fit'):
            # TensorFlow training
            self.model.fit(
                X, y_encoded,
                epochs=10,
                batch_size=32,
                validation_split=0.2,
                verbose=1
            )
        else:
            # Sklearn training (binarize predictions)
            y_multi = np.where(y_encoded.sum(axis=1, keepdims=True) > 0, y_encoded, 1.0)
            self.model.fit(X, y_multi)
        
        self.is_fitted = True
        print(f"✓ Classifier trained on {len(self.code_list)} codes")
        
        # Save config
        os.makedirs("models", exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump({"codes": self.code_list, "embedding_dim": self.embedding_dim}, f)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> list[list[tuple[str, float]]]:
        """
        Predict codes for embeddings
        
        Returns: List of [(code, confidence), ...]
        """
        if not self.is_fitted or self.model is None:
            return [[] for _ in range(len(X))]
        
        # Get predictions
        if self.tf and hasattr(self.model, 'predict'):
            probs = self.model.predict(X, verbose=0)
        else:
            probs = self.model.predict_proba(X)
        
        # Format results
        results = []
        for prob_row in probs:
            codes = [
                (code, float(prob))
                for code, prob in zip(self.code_list, prob_row)
                if prob >= threshold
            ]
            codes.sort(key=lambda x: x[1], reverse=True)
            results.append(codes[:10])  # Top 10
        
        return results

    def load(self, model_path: str) -> None:
        """Load trained classifier"""
        if self.tf and os.path.exists(model_path):
            self.model = self.tf.keras.models.load_model(model_path)
            self.is_fitted = True
            
            # Load config
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    self.code_list = config["codes"]
                    self.mlb.fit([self.code_list])
            
            print(f"✓ Classifier loaded from {model_path}")

    def save(self, model_path: str) -> None:
        """Save trained classifier"""
        if self.model and self.tf:
            self.model.save(model_path)
            print(f"✓ Classifier saved to {model_path}")
