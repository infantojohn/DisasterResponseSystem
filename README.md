# AI-Powered Disaster Response and Resource Allocation Platform

An AI-powered disaster management system that analyzes citizen emergency reports, classifies disaster types, predicts incident priorities, and supports rescue-team allocation using FastAPI and MongoDB.

## Overview

During natural disasters and other emergencies, authorities need to identify critical incidents, understand the needs of affected people, and coordinate rescue resources efficiently.

This project provides a platform where citizens can submit incident reports and authorities can review incidents, assess their urgency, assign rescue teams, and update incident statuses. AI-based analysis supports decision-making, while MongoDB stores incident information and related operational data.

## Key Features

### AI Functionalities

- **Disaster-Type Classification:** Predicts the disaster category from a submitted report.
- **Incident Priority Prediction:** Uses a machine-learning model to estimate incident priority.
- **Priority Refinement:** Applies rule-based checks using extracted information about affected, trapped, and injured people.
- **Emergency Information Extraction:** Extracts relevant information from incident descriptions.
- **Related-Incident Detection:** Identifies potentially related reports.
- **Resource Recommendation:** Suggests resources based on the predicted disaster type, priority, and reported needs.

### Incident and Rescue Management

- Citizen-facing incident reporting.
- Authority dashboard for reviewing incidents.
- Incident search and filtering.
- Rescue-team listing and assignment.
- Incident status management.
- Incident status-history tracking.
- Live incident updates, where configured.

### MongoDB Functionalities

- Incident and rescue-team document storage.
- Incident retrieval and updates.
- Dashboard statistics using aggregation.
- Incident status-history storage.
- Geospatial location data for rescue teams.
- MongoDB Change Streams for monitoring incident changes, where configured.

## Technology Stack

- **Programming Language:** Python
- **Backend:** FastAPI
- **Database:** MongoDB
- **Machine Learning:** scikit-learn
- **Text Processing:** TF-IDF Vectorization
- **Classification Algorithm:** Logistic Regression
- **Model Persistence:** Joblib
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
DisasterResponseSystem/
├── ai/          # AI models, training, and analysis
├── backend/     # FastAPI backend and API endpoints
├── data/        # Dataset used for model training and evaluation
├── database/    # Database-related files and operations
├── frontend/    # Citizen and authority interfaces
├── .gitignore
└── README.md
```

The exact files and responsibilities may vary according to the current implementation.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/infantojohn/DisasterResponseSystem.git
cd DisasterResponseSystem
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

If it is not available yet, create one containing the project's actual dependencies before following this step.

### 4. Configure MongoDB

Create or select a MongoDB database and configure the connection string through environment variables in a local `.env` file, using the variable names expected by the backend.

**Security:** Never commit your `.env` file, database credentials, or API keys to GitHub.

### 5. Start the Backend

From the project root, run:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0
```

If your FastAPI application uses a different module path, adjust the command accordingly.

Open the interactive API documentation at:

http://127.0.0.1:8000/docs

### 6. Open the Frontend

Open the relevant frontend HTML files using your configured local development server. Ensure the backend URL in the frontend matches the address and port where FastAPI is running.

## Machine-Learning Models

The project uses text-based machine-learning models for disaster classification and incident-priority prediction.

The training workflow uses TF-IDF to represent report text and Logistic Regression to perform classification. Trained model files are loaded by the application for inference.

Model performance should be evaluated using held-out test data. Evaluation results reflect the available dataset and do not guarantee performance in real-world emergencies.

## Database Design

The project uses MongoDB collections to organize operational data, including:

- `incidents` — submitted reports and incident details.
- `rescue_teams` — rescue-team information and location data.
- `incident_status_history` — records of incident status changes.

Actual collection fields depend on the implemented database schema.

## Future Enhancements

- Citizen-facing incident progress tracking.
- Improved extraction of emergency details from natural-language reports.
- More comprehensive model training and evaluation.
- Verified nearest-team selection using MongoDB geospatial queries.
- Enhanced real-time notifications and operational monitoring.

## Important Note

This project is intended as an academic and software-engineering project to support disaster-response workflows. AI predictions and resource recommendations should assist, not replace, decisions made by trained emergency-response personnel.

## Author

**Infanto John**  
B.Tech Computer Science and Engineering  
Vellore Institute of Technology (VIT)

## License

No license has been specified yet. All rights remain with the repository owner unless a license is added.
