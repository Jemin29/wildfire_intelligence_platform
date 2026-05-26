# Contributing

Thanks for your interest in contributing. This project welcomes bug fixes, documentation improvements, and new features.

## Quick Rules

- Be respectful and collaborative.
- Open an issue before large changes.
- Keep PRs focused and small.

## Development Setup

```powershell
python -m venv .venv
\.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Branch Strategy

- `main`: stable, production-ready
- `dev`: integration branch for active work
- `feature/*`: feature branches
- `fix/*`: bug fix branches

## Commit Messages

Use clear, action-oriented messages:

- feat: add weather ingestion pipeline
- fix: handle missing model artifact
- docs: expand deployment guide
- chore: update dependencies

## Testing

```powershell
pytest
```

## Pull Requests

- Include a short description and testing notes.
- Update documentation where relevant.
- Add or update tests for code changes.

## Code Style

- Keep functions small and focused.
- Prefer explicit naming over cleverness.
- Avoid breaking changes without discussion.
