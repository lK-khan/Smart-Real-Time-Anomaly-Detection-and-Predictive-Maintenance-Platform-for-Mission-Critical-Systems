Smart Real‑Time Anomaly Detection & Predictive Maintenance Platform

An end‑to‑end AI/ML system that simulates sensor data, detects anomalies, predicts failures, and visualizes results in real time—all packaged in Docker containers for reproducible demos.

🚀 Features

Data Simulation: Python script generates realistic temperature & pressure readings with injected anomalies and failure events.

Ingestion API: Flask service applies rule‑based and ML‑based anomaly detection, calculates failure probability, and logs data.

Failure‑Prediction Model: Random Forest classifier trained on simulated failure‑labeled data.

Live Dashboard: Dash app displaying temperature, pressure, anomalies, and failure risk with dual‑axis charts.

Containerized: Dockerized simulator, API, and dashboard, orchestrated via Docker Compose.

🏗 Architecture

+--------------+     HTTP POST      +-----------+     Shared CSV      +-----------+
|  Simulator   |  ----------------> |   API     |  -----------------> | Dashboard |
| (simulate_…) |                     | (ingest)  |                     | (dashboard)
+--------------+                     +-----------+                     +-----------+

Simulator sends JSON to api:5000

API writes sensor_data.csv in shared volume /data

Dashboard polls the same CSV and updates plots

🛠 Quick Start

Clone the repo:

git clone https://github.com/lK-khan/Smart-Real-Time-Anomaly-Detection-and-Predictive-Maintenance-Platform-for-Mission-Critical-Systems.git
cd Smart-Real-Time-Anomaly-Detection-and-Predictive-Maintenance-Platform-for-Mission-Critical-Systems

2. **Bring up the containers** (requires Docker & Compose):
   ```bash
docker compose build
docker compose up -d

View the dashboard:Open your browser at http://localhost:8050 to see live sensor data and predictions.

Test the API (optional):



curl -X POST http://localhost:5000/ingest -H "Content-Type: application/json" -d '{"sensor_id":"sensor_test","timestamp":"2025-04-21T12:00:00","temperature":30,"pressure":1.0,"anomaly":0,"failure":0}'


---

## 📦 Repository Structure


├── simulate_data.py       # Sensor data generator
├── ingest.py              # Flask ingestion API
├── dashboard.py           # Dash live dashboard
├── train_model.py         # Train ML anomaly detector
├── train_failure_model.py # Train failure-prediction model
├── Dockerfile.api         # Dockerfile for API service
├── Dockerfile.dash        # Dockerfile for Dashboard service
├── Dockerfile.sim         # Dockerfile for Simulator
├── requirements-*.txt     # Python dependencies
├── docker-compose.yml     # Compose orchestration
├── *.joblib               # Serialized models & preprocessors
└── README.md              # Project overview & instructions


---

## 📈 Model Performance

- **Anomaly Detection**: Random Forest reached 100% precision & recall on test splits.  
- **Failure Prediction**: Initial run shows high accuracy on imbalanced data; consider oversampling/feature engineering for production.

---

## 🔮 Future Work

- **Feature Engineering**: Rolling-window stats, time-since-last-anomaly for better failure predictions.  
- **CI/CD**: GitHub Actions for linting, testing, and automated Docker builds.  
- **Kubernetes**: Deploy services on a managed cluster (EKS/GKE).  
- **Alerting**: Integrate email/SMS notifications for high failure risk.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
