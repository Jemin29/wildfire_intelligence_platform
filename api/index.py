from app.core.app_factory import create_app

app = create_app()

# Vercel expects a module-level "app" for Python serverless functions.
