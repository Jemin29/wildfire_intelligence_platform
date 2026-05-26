# Vercel Deployment (Static Dashboard)

## Steps

1. Login to Vercel and create a new project from the GitHub repo.
2. Select `Other` framework preset.
3. Set the output directory to `static` (if you want the HTML dashboard).
4. Add environment variables if needed.
5. Deploy and grab the public URL.

## Notes

- If you want the dashboard from `templates/`, build a static export or a React app.
- Update `CORS_ORIGINS` on the backend to the Vercel domain.
