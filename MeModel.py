import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import numpy as np


class Vectorizer: 
    def __init__(self):
        self.features_idx = {}
    
    def fit(self, X):
        idx = 0
        for features in X:
            for key, value in features.items():
                feature_key = f"{key}={value}"
                if feature_key not in self.features_idx:
                    self.features_idx[feature_key] = idx
                    idx += 1
        print(self.features_idx)
        return self
    
    def transform(self, X):
        output = np.zeros((len(X), len(self.features_idx)))
        row = 0
        for features in X: 
            for key, value in features.items():
                feature_key = f"{key}={value}"
                if feature_key in self.features_idx:
                    col = self.features_idx[feature_key]
                    output[row, col] = 1
            row += 1
        return output

def trainModel(feature_file_path, model_output_path):

    features_list = []
    labels_list = []

    print(f"Reading features from {feature_file_path}...")
    with open(feature_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|||')
            if len(parts) < 2:
                continue

            label = parts[0].strip()
            features = {}

            features_str = parts[1].strip()

            for feature in features_str.split(' '):

                try:
                    key, value = feature.split('=')
                    key = key.strip()
                    value = value.strip()
                    features[key] = value
                except ValueError:
                    continue # Skip malformed features
            
            labels_list.append(label)
            features_list.append(features)

    if not labels_list:
        print("No features were loaded. Exiting.")
        return

    print(f"Loaded {len(labels_list)} samples.")


    # Train the model
    print("Training the reordering model...")
    print(features_list)
    print(labels_list)

    vectorizer = Vectorizer()
    vectorized_features = vectorizer.fit(features_list).transform(features_list)
    print(vectorized_features)

    lg_model = LogisticRegression(max_iter=1000, multi_class='multinomial')
    lg_model.fit(vectorized_features, labels_list)
    joblib.dump({"vectorizer": vectorizer, "model": lg_model}, model_output_path)

