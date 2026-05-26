# AI-Powered Wildfire Intelligence Platform

AI-powered wildfire intelligence and disaster analytics platform with machine learning, real-time monitoring, weather intelligence, geospatial risk mapping, and predictive analytics.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![CI](https://github.com/Jemin29/wildfire_intelligence_platform/actions/workflows/ci.yml/badge.svg)](#ci)
[![Deploy](https://img.shields.io/badge/deploy-ready-informational.svg)](#deployment)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](#tech-stack)

## Overview

This platform aggregates weather signals, geospatial data, and model predictions into a single operational dashboard. It provides alerting, analytics, and risk scoring to help responders and stakeholders monitor wildfire risk in real time.

## Tech Stack

- Flask, Jinja, HTML/CSS/JavaScript
- PostgreSQL + SQLAlchemy
- Scikit-learn, XGBoost
- Folium maps for geospatial visualization
- Weather APIs for live signals

## Architecture

```mermaid
flowchart LR
	subgraph Client
		UI[Dashboard UI]
	end
	subgraph API
		Flask[Flask API]
		ML[Model Inference]
		Jobs[Batch Analytics]
	end
	subgraph Data
		DB[(PostgreSQL)]
		Weather[Weather APIs]
		Geo[Geo Datasets]
	end

	UI -->|REST| Flask
	Flask --> ML
	Flask --> DB
	Jobs --> DB
	ML --> DB
	Flask --> Weather
	Flask --> Geo
```

## Setup

### Prerequisites

- Python 3.11
- PostgreSQL 14+
- Docker (optional)

### Local Development (Windows PowerShell)

```powershell
python -m venv .venv
\.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
flask run
```

### Environment Variables

Create a `.env` file in the project root:

```
FLASK_ENV=development
SECRET_KEY=replace_me
JWT_SECRET_KEY=replace_me
DATABASE_URL=postgresql://user:pass@localhost:5432/wildfire
MODEL_PATH=models/model.pkl
WEATHER_API_KEY=replace_me
CORS_ORIGINS=http://localhost:3000
```

## API Documentation

Base URL: `http://localhost:5000`

| Endpoint | Method | Description |
| --- | --- | --- |
| /api/health | GET | Service health check |
| /api/predict | POST | Model prediction |
| /api/weather | GET | Current weather signals |
| /api/alerts | GET | Active alerts |

## Deployment

See [docs/deployment.md](docs/deployment.md) and [docs/render.md](docs/render.md) for Render/Vercel workflows. Docker instructions are in [docs/docker.md](docs/docker.md).

## Screenshots

Add screenshots to `docs/screenshots/` and update the links below.

- Dashboard overview: `docs/screenshots/dashboard.png`
- Risk map: `docs/screenshots/risk-map.png`
- Alert feed: `docs/screenshots/alerts.png`

## Roadmap

- [ ] Stream ingestion for near-real-time weather updates
- [ ] Alert prioritization using dynamic thresholds
- [ ] Model monitoring and drift detection
- [ ] Role-based access and audit logging
- [ ] Mobile-responsive analytics dashboard

## Future Scope

- Wildfire spread simulation module
- Satellite imagery integration
- Multi-region fire response coordination
- Automated dispatch and incident management hooks

## Repository Structure

- app/: Flask application and APIs
- templates/: Jinja templates
- static/: JS/CSS assets
- docs/: architecture and deployment guides
- models/: trained model artifacts
- notebooks/: experiments and analysis
- tests/: unit and integration tests
- scripts/: ETL and maintenance scripts

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and standards.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## CI

Recommended: GitHub Actions running lint + tests on every PR and `main` push.
