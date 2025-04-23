# import numpy as np
# import random
# from datetime import datetime
# import time
# import requests  # This is needed to send the POST request

# def generate_sensor_data():
#     sensor_id = random.choice(['sensor_1', 'sensor_2', 'sensor_3'])
#     timestamp = datetime.utcnow().isoformat()
#     temperature = np.random.normal(25, 2)
#     pressure = np.random.normal(1, 0.1)

#     if np.random.rand() > 0.95:
#         temperature *= random.uniform(1.5, 2)

#     return {
#         "sensor_id": sensor_id,
#         "timestamp": timestamp,
#         "temperature": round(temperature, 2),
#         "pressure": round(pressure, 2)
#     }

# if __name__ == "__main__":
#     API_URL = "http://127.0.0.1:5000/ingest"  # Your local Flask endpoint

#     while True:
#         data_point = generate_sensor_data()
#         print("Sending:", data_point)

#         try:
#             response = requests.post(API_URL, json=data_point)
#             if response.status_code == 200:
#                 print("✅ Successfully sent.")
#             else:
#                 print(f"❌ Failed with status code: {response.status_code}")
#         except Exception as e:
#             print(f"❗ Error sending data: {e}")

#         time.sleep(1)

import numpy as np
import random
from datetime import datetime
import time
import requests

#API_URL = "http://127.0.0.1:5000/ingest"
API_URL = "http://api:5000/ingest"
def generate_sensor_data():
    sensor_id = random.choice(['sensor_1', 'sensor_2', 'sensor_3'])
    timestamp = datetime.utcnow().isoformat()
    temperature = np.random.normal(25, 2)
    pressure    = np.random.normal(1, 0.1)

    # Rule‑based anomaly detection locally in simulator
    if not (15 <= temperature <= 35) or not (0.8 <= pressure <= 1.2):
        anomaly_flag = 1
    else:
        anomaly_flag = 0

    return {
        "sensor_id": sensor_id,
        "timestamp": timestamp,
        "temperature": round(temperature, 2),
        "pressure":    round(pressure, 2),
        "anomaly":     anomaly_flag
    }

if __name__ == "__main__":
    while True:
        data_point = generate_sensor_data()

        # Simulate a “failure” event with 5% probability right after an anomaly
        if data_point["anomaly"] == 1 and random.random() < 0.05:
            data_point["failure"] = 1
        else:
            data_point["failure"] = 0

        # Send to your Flask API
        try:
            resp = requests.post(API_URL, json=data_point)
            if resp.status_code != 200:
                print("❌ Ingestion failed:", resp.text)
            else:
                print("✅ Successfully sent:", resp.text)
        except Exception as e:
            print("❗ Error:", e)

        time.sleep(1)
