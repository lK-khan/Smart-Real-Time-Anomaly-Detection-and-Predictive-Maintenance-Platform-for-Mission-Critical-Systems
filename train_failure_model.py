# train_failure_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# 1. Load the labeled data
df = pd.read_csv('sensor_data.csv')

# 2. Prepare label and features
#   - Use the simulator’s 'failure' column as the target
#   - Include the rule_anomaly flag as a feature, plus raw sensor readings
df['rule_flag'] = df['rule_anomaly'].map({'Yes': 1, 'No': 0})
y = df['failure']

# 3. One‑hot encode sensor_id
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
sensor_ohe = ohe.fit_transform(df[['sensor_id']])
sensor_cols = ohe.get_feature_names_out(['sensor_id'])
df_ohe = pd.DataFrame(sensor_ohe, columns=sensor_cols)

# 4. Assemble feature matrix
X = pd.concat([
    df[['temperature', 'pressure', 'rule_flag']].reset_index(drop=True),
    df_ohe.reset_index(drop=True)
], axis=1)

# 5. Scale numeric columns
scaler = StandardScaler()
X[['temperature', 'pressure']] = scaler.fit_transform(X[['temperature', 'pressure']])

# 6. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 7. Train a classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 8. Evaluate performance
y_pred = clf.predict(X_test)
print("\nFailure‑Prediction Model Performance:\n")
print(classification_report(y_test, y_pred, digits=4))

# 9. Save the model and preprocessors
joblib.dump(clf,   'fail_clf.joblib')
joblib.dump(ohe,   'sensor_ohe_fp.joblib')
joblib.dump(scaler,'scaler_fp.joblib')

print("\n✅ Saved:\n  • fail_clf.joblib\n  • sensor_ohe_fp.joblib\n  • scaler_fp.joblib")
