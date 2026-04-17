# Container Crash Detection System 🚢

An ML-powered real-time monitoring and analysis system for container sensor data, designed to detect crashes and assess impact severity during transport.

## 🚀 Overview

The **Container Crash Detection System** provides a professional dashboard for logistics monitoring. It uses synthetic sensor signals (simulating accelerometer data) and a Machine Learning model to classify events into "Normal", "Warning", or "Critical" status.

### Key Features
- **📊 Signal Analysis**: Simulate and analyze specific event types with high-confidence ML predictions.
- **📡 Live Streaming**: Real-time visualization of sensor data streams with instantaneous detection.
- **📜 Event History**: Persistent logging of all detected anomalies in a dedicated database.
- **🚦 Severity Assessment**: Visual indicators (gauges and bars) for impact severity and prediction confidence.
- **💎 Premium UI**: Modern, responsive dashboard built with Streamlit and Plotly.

## 📂 Project Structure

```text
├── config/             # System configuration and global settings
├── dashboard/          # Streamlit UI components (views, gauges, widgets)
├── database/           # SQLite database logic and event logging
├── models/             # ML model training scripts and exported .pkl files
├── sensors/            # Signal generation and feature engineering
├── services/           # Core detection engine and alert logic
├── utils/              # General helper functions
├── app.py              # Main Streamlit application entry point
├── requirements.txt    # Python dependency list
└── README.md           # Project documentation
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.10 or higher
- Git (optional, for cloning)

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd "Container crash detection system"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 How to Run

To launch the Streamlit dashboard, run the following command from the project root:

```bash
streamlit run app.py
```

Once the server starts, you can access the dashboard in your browser at `http://localhost:8501`.

## Alpha Testing

An initial alpha test suite is included under `tests/` to validate syntax and core behaviors across the project modules.

Run all tests with:

```bash
pytest -q
```

Run only alpha smoke coverage:

```bash
pytest -q tests/test_alpha_smoke_all_files.py
```

## 🧠 Machine Learning

The system uses a Scikit-Learn based model trained on engineered features from accelerometer signals. Features include:
- Signal mean and standard deviation
- Peak values (max/min)
- Zero-crossing rate
- Root-mean-square (RMS) levels

The model classifies events into:
- **0 - Normal**: Routine transport vibration.
- **1 - Warning**: Mild impact or container shift.
- **2 - Critical**: Severe crash or high-impact collision.

---
*Developed as part of a Final Year Project.*
