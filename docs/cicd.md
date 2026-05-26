# CI/CD Recommendations

## Minimal Pipeline

- Lint + unit tests on pull requests.
- Build Docker image on main.
- Run smoke tests against the container.
- Deploy to Render using GitHub integration.

## Suggested GitHub Actions Steps

1. Checkout code
2. Set up Python
3. Install requirements
4. Run `pytest`
5. Build Docker image
6. Deploy (Render hook)
