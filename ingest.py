# # from flask import Flask, request, jsonify
# # import csv
# # import os

# # app = Flask(__name__)

# # DATA_FILE = 'sensor_data.csv'

# # # Initialize CSV file with header if it doesn't exist
# # if not os.path.exists(DATA_FILE):
# #     with open(DATA_FILE, mode='w', newline='') as csvfile:
# #         writer = csv.writer(csvfile)
# #         writer.writerow(["sensor_id", "timestamp", "temperature", "pressure", "anomaly", "anomaly_reason"])

# # # --- Anomaly Detection Logic ---
# # def is_anomalous(data):
# #     temp = data.get('temperature')
# #     pressure = data.get('pressure')

# #     # Define basic anomaly thresholds
# #     if not (15 <= temp <= 35):
# #         return True, "Temperature anomaly"
# #     if not (0.8 <= pressure <= 1.2):
# #         return True, "Pressure anomaly"
# #     return False, None

# # # Function to log data to CSV
# # def log_data(data, anomaly_flag, anomaly_reason):
# #     with open(DATA_FILE, mode='a', newline='') as csvfile:
# #         writer = csv.writer(csvfile)
# #         writer.writerow([
# #             data.get("sensor_id"),
# #             data.get("timestamp"),
# #             data.get("temperature"),
# #             data.get("pressure"),
# #             "Yes" if anomaly_flag else "No",
# #             anomaly_reason if anomaly_reason else ""
# #         ])

# # # --- Ingestion Endpoint ---
# # @app.route('/ingest', methods=['POST'])
# # def ingest():
# #     data = request.get_json()
# #     print(f"Received data: {data}")

# #     anomaly, reason = is_anomalous(data)
# #     if anomaly:
# #         print(f"⚠️ ALERT: {reason} detected in sensor {data['sensor_id']} at {data['timestamp']}")
# #         print(f"Anomalous Data: {data}")

# #     # Log the received data along with anomaly info
# #     log_data(data, anomaly, reason)

# #     return jsonify({"status": "success", "data": data})

# # # --- Main Entry Point ---
# # if __name__ == '__main__':
# #     app.run(debug=True)

# # ingest.py

# from flask import Flask, request, jsonify
# import csv, os
# import joblib
# import pandas as pd

# app = Flask(__name__)

# DATA_FILE = 'sensor_data.csv'

# # --- Load ML artifacts ---
# clf    = joblib.load('anomaly_clf.joblib')
# ohe    = joblib.load('sensor_ohe.joblib')
# scaler = joblib.load('scaler.joblib')

# # --- Initialize CSV with expanded header if needed ---
# if not os.path.exists(DATA_FILE):
#     with open(DATA_FILE, mode='w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             "sensor_id",
#             "timestamp",
#             "temperature",
#             "pressure",
#             "rule_anomaly",
#             "rule_reason",
#             "ml_anomaly"
#         ])

# # --- Rule‑based anomaly detection ---
# def is_anomalous_rule(data):
#     temp     = data['temperature']
#     pressure = data['pressure']
#     if not (15 <= temp <= 35):
#         return True, "Temperature anomaly"
#     if not (0.8 <= pressure <= 1.2):
#         return True, "Pressure anomaly"
#     return False, None

# # --- Log everything to CSV ---
# def log_data(data, rule_flag, rule_reason, ml_flag):
#     with open(DATA_FILE, mode='a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             data["sensor_id"],
#             data["timestamp"],
#             data["temperature"],
#             data["pressure"],
#             "Yes" if rule_flag else "No",
#             rule_reason or "",
#             "Yes" if ml_flag else "No"
#         ])

# # --- Ingestion endpoint ---
# @app.route('/ingest', methods=['POST'])
# def ingest():
#     data = request.get_json()
#     print(f"Received data: {data}")

#     # 1. Rule‑based check
#     rule_flag, rule_reason = is_anomalous_rule(data)
#     if rule_flag:
#         print(f"⚠️ RULE ALERT: {rule_reason} detected in sensor {data['sensor_id']} at {data['timestamp']}")

#     # 2. ML‑based prediction
#     # Prepare a single‑row DataFrame
#     df_new = pd.DataFrame([{
#         "sensor_id":   data["sensor_id"],
#         "temperature": data["temperature"],
#         "pressure":    data["pressure"]
#     }])
#     # Encode sensor_id
#     sensor_enc = ohe.transform(df_new[["sensor_id"]])
#     sensor_cols = ohe.get_feature_names_out(["sensor_id"])
#     df_sensor  = pd.DataFrame(sensor_enc, columns=sensor_cols)
#     # Scale numeric features
#     df_new[["temperature","pressure"]] = scaler.transform(df_new[["temperature","pressure"]])
#     # Combine features
#     X_new = pd.concat([
#         df_new[["temperature","pressure"]].reset_index(drop=True),
#         df_sensor.reset_index(drop=True)
#     ], axis=1)
#     ml_pred = clf.predict(X_new)[0]
#     if ml_pred == 1:
#         print(f"🤖 ML ALERT: Anomaly predicted for sensor {data['sensor_id']} at {data['timestamp']}")

#     # 3. Log to CSV
#     log_data(data, rule_flag, rule_reason, ml_pred == 1)

#     # 4. Respond with both flags
#     return jsonify({
#         "status":       "success",
#         "data":         data,
#         "rule_anomaly": bool(rule_flag),
#         "ml_anomaly":   bool(ml_pred)
#     })

# # --- Run the app ---
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify
import csv, os
import joblib
import pandas as pd

app = Flask(__name__)

DATA_FILE = '/data/sensor_data.csv'

# --- Load ML artifacts (for rule + ML anomaly) ---
clf    = joblib.load('anomaly_clf.joblib')
ohe    = joblib.load('sensor_ohe.joblib')
scaler = joblib.load('scaler.joblib')
# after your existing joblib imports
fail_clf   = joblib.load('fail_clf.joblib')
fp_ohe     = joblib.load('sensor_ohe_fp.joblib')
fp_scaler  = joblib.load('scaler_fp.joblib')


# --- Initialize CSV with expanded header if needed ---
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "sensor_id",
            "timestamp",
            "temperature",
            "pressure",
            "rule_anomaly",
            "rule_reason",
            "ml_anomaly",
            "failure",
            "failure_prob"
        ])

# --- Rule‑based anomaly detection ---
def is_anomalous_rule(data):
    temp     = data['temperature']
    pressure = data['pressure']
    if not (15 <= temp <= 35):
        return True, "Temperature anomaly"
    if not (0.8 <= pressure <= 1.2):
        return True, "Pressure anomaly"
    return False, None

# --- Log everything to CSV ---
def log_data(data, rule_flag, rule_reason, ml_flag, failure_flag, failure_prob):
    with open(DATA_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data["sensor_id"],
            data["timestamp"],
            data["temperature"],
            data["pressure"],
            "Yes" if rule_flag else "No",
            rule_reason or "",
            "Yes" if ml_flag else "No",
            failure_flag,
            f"{failure_prob:.2f}"
        ])

# --- Ingestion endpoint ---
@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.get_json()
    print(f"Received data: {data}")

    # 1. Rule‑based anomaly check
    rule_flag, rule_reason = is_anomalous_rule(data)
    if rule_flag:
        print(f"⚠️ RULE ALERT: {rule_reason} in {data['sensor_id']} at {data['timestamp']}")

    # 2. ML‑based anomaly prediction
    df_new = pd.DataFrame([{
        "sensor_id":   data["sensor_id"],
        "temperature": data["temperature"],
        "pressure":    data["pressure"]
    }])
    sensor_enc = ohe.transform(df_new[["sensor_id"]])
    sensor_cols = ohe.get_feature_names_out(["sensor_id"])
    df_sensor  = pd.DataFrame(sensor_enc, columns=sensor_cols)
    df_new[["temperature","pressure"]] = scaler.transform(df_new[["temperature","pressure"]])
    X_new = pd.concat([
        df_new[["temperature","pressure"]].reset_index(drop=True),
        df_sensor.reset_index(drop=True)
    ], axis=1)
    ml_pred = clf.predict(X_new)[0]
    if ml_pred == 1:
        print(f"🤖 ML ALERT: Anomaly predicted for {data['sensor_id']} at {data['timestamp']}")

    # 3. Grab the simulator’s failure flag (default to 0 if missing)
    failure_flag = data.get("failure", 0)
    if failure_flag:
        print(f"🔴 FAILURE EVENT: sensor {data['sensor_id']} reported FAILURE at {data['timestamp']}")

    # Prepare features for failure‐prediction
    df_fp = pd.DataFrame([{
        'sensor_id':  data['sensor_id'],
        'temperature': data['temperature'],
        'pressure':    data['pressure'],
        'rule_flag':   1 if rule_flag else 0
    }])
    enc = fp_ohe.transform(df_fp[['sensor_id']])
    df_enc = pd.DataFrame(enc, columns=fp_ohe.get_feature_names_out(['sensor_id']))
    df_fp[['temperature','pressure']] = fp_scaler.transform(df_fp[['temperature','pressure']])
    X_fp = pd.concat([df_fp[['temperature','pressure','rule_flag']], df_enc], axis=1)

    # Predict failure probability
    fail_prob = fail_clf.predict_proba(X_fp)[0][1]
    if fail_prob > 0.5:
        print(f"🔴 FAILURE RISK HIGH ({fail_prob:.2f}) for {data['sensor_id']} at {data['timestamp']}")

    # Finally, log everything (including fail_prob):
    log_data(data, rule_flag, rule_reason, ml_pred==1, failure_flag, fail_prob)

    # And return the risk score in your JSON:
    return jsonify({
        "status":       "success",
        "data":         data,
        "rule_anomaly": bool(rule_flag),
        "ml_anomaly":   bool(ml_pred),
        "failure":      bool(failure_flag),
        "failure_prob": round(fail_prob, 2)
    })


    # 4. Log everything
    log_data(data, rule_flag, rule_reason, ml_pred == 1, failure_flag)

    # 5. Respond with all flags
    return jsonify({
        "status":        "success",
        "data":          data,
        "rule_anomaly":  bool(rule_flag),
        "ml_anomaly":    bool(ml_pred),
        "failure":       bool(failure_flag)
    })

if __name__ == '__main__':
    # app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', debug=True, port=5000)