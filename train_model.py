# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# 1. Load data
df = pd.read_csv('sensor_data.csv')

# 2. Preprocess
# a) Create binary label from anomaly column
df['label'] = df['anomaly'].map({'Yes': 1, 'No': 0})

# b) One‑hot encode sensor_id
# Use the exact column name 'sensor_id'
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
sensor_ohe = ohe.fit_transform(df[['sensor_id']])
# Retrieve the generated feature names
sensor_cols = ohe.get_feature_names_out(['sensor_id'])
df_ohe = pd.DataFrame(sensor_ohe, columns=sensor_cols)

# c) Combine features
X = pd.concat([
    df[['temperature', 'pressure']].reset_index(drop=True),
    df_ohe.reset_index(drop=True)
], axis=1)
y = df['label']

# d) Scale numeric features
scaler = StandardScaler()
X[['temperature', 'pressure']] = scaler.fit_transform(X[['temperature', 'pressure']])

# 3. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# 4. Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 5. Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits=4))

# 6. Save model and preprocessing objects
joblib.dump(clf, 'anomaly_clf.joblib')
joblib.dump(ohe, 'sensor_ohe.joblib')
joblib.dump(scaler, 'scaler.joblib')

print("✅ Model, encoder, and scaler saved:")
print("   • anomaly_clf.joblib")
print("   • sensor_ohe.joblib")
print("   • scaler.joblib")
