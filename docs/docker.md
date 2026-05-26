# Docker Setup

## Build

```bash
docker build -t wildfire-api .
```

## Run

```bash
docker run --env-file .env -p 8000:8000 wildfire-api
```

## Compose

```bash
docker-compose up --build
```
