# Render Deployment (Backend + Postgres)

## Backend

1. Create a Web Service on Render.
2. Select `Docker` and point to `Dockerfile`.
3. Add environment variables from `.env.example`.
4. Attach the Postgres database and map `DATABASE_URL`.

## Postgres

- Use the managed Render Postgres instance.
- Run migrations with `flask db upgrade` after first deploy.

## Health Check

- Configure Render health check to `GET /api/health`.
