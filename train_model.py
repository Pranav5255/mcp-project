import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Load data
df = pd.read_csv('clothing_combinations.csv')

# Encode categorical features
encoders = {}
for column in ['top_type', 'top_color', 'bottom_type', 'bottom_color']:
    le = LabelEncoder()
    df[column + '_encoded'] = le.fit_transform(df[column])
    encoders[column] = le

# Prepare features and target
X = df[['top_type_encoded', 'top_color_encoded', 'bottom_type_encoded', 'bottom_color_encoded']]
y = df['good_combination']

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model and encoders
with open('clothing_combo_model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('encoders.pkl', 'wb') as file:
    pickle.dump(encoders, file)

print("Model trained and saved successfully!")