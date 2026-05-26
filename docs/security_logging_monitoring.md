# Security, Logging, and Monitoring

## Security Best Practices

- Store secrets only in env vars or secret managers.
- Enable HTTPS-only traffic in Render and Vercel.
- Rotate API keys regularly and never log them.
- Restrict `CORS_ORIGINS` to trusted domains.
- Use least-privilege DB users and rotate credentials.

## Logging

- Use structured logs with timestamps (already configured).
- Track request IDs for inference flows.
- Separate error logs for alert failures and weather API failures.

## Monitoring

- Use Render built-in health checks and alerts.
- Add uptime monitoring via external service.
- Track model inference latency and error rates.
