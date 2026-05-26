# Deployment Workflow

## Deployment Architecture

- **Backend**: Flask + Gunicorn in a Docker container
- **Database**: PostgreSQL managed by Render
- **Frontend**: Static dashboard (HTML/CSS/JS) hosted on Vercel
- **Observability**: Render logs + optional external monitoring

## Step-by-Step Guide

### 1) Prepare Environment Variables

Required production variables:

- `FLASK_ENV=production`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `MODEL_PATH`
- `WEATHER_API_KEY`
- `CORS_ORIGINS`

### 2) Build and Test Locally (Docker)

```bash
docker build -t wildfire-api .
docker run --env-file .env -p 8000:8000 wildfire-api
```

### 3) Deploy Backend on Render (Docker)

1. Push the repository to GitHub.
2. In Render, create a new Web Service from the repo.
3. Select Docker and set the service to use `Dockerfile`.
4. Add environment variables in the Render dashboard.
5. Attach a Render Postgres instance and map `DATABASE_URL`.

### 4) Deploy Frontend on Vercel

1. Create a new Vercel project.
2. Select `Other` framework and deploy the repo.
3. Set the build output to `static/` if using the HTML dashboard.
4. Update `CORS_ORIGINS` on the backend to the Vercel domain.

### 5) Validate Production

- `GET /api/health`
- `POST /api/predict`
- `GET /api/weather`

## Gunicorn Setup

- Uses `gthread` worker class for I/O + CPU balance.
- `-w 3` should be tuned based on CPU cores.

## Procfile

Render and Heroku-style deployments can run:

```
web: gunicorn -w 3 -k gthread -t 120 -b 0.0.0.0:$PORT wsgi:app
```

## CI/CD Recommendations

- Run `pytest` on every pull request.
- Build Docker images and run smoke tests.
- Use GitHub Actions to auto-deploy to Render on main.

## Production Optimization Tips

- Enable caching for weather API responses.
- Use database indexes on time and geo columns.
- Rotate logs, limit PII, and encrypt secrets.
- Add health checks and auto-restart policies.
