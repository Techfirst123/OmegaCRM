# OmegaERP

OmegaERP is a Django-based ERP workspace for vendor registration, project distribution, material master management, and vendor-facing material quotation workflows.

This repository is now prepared for:

- GitHub source control
- environment-based configuration
- PostgreSQL in production
- WhiteNoise static file serving
- Gunicorn-based deployment

## Stack

- Python 3.14+
- Django 6.0.5
- PostgreSQL
- Gunicorn
- WhiteNoise
- django-environ

## Repository Hygiene

The repo is configured to ignore local-only and sensitive artifacts including:

- `.venv/`, `venv/`
- `**/__pycache__/`
- `*.pyc`
- `.env`
- `db.sqlite3`
- `media/`
- `node_modules/`
- `.vscode/`

## Environment Variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

Required keys:

- `DJANGO_SETTINGS_MODULE`
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `OPENAI_API_KEY`
- `THIRD_PARTY_API_KEY`

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql://postgres:your-password@127.0.0.1:5432/omegadb
```

## Settings Layout

Environment-specific settings live here:

```text
omegaerp/
  settings/
    __init__.py
    base.py
    development.py
    production.py
```

Use:

- `omegaerp.settings.development` for local development
- `omegaerp.settings.production` for production

## Local Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env`.
4. Run migrations:

```bash
python manage.py migrate
```

If you already have existing PostgreSQL tables created before migrations were committed, use:

```bash
python manage.py migrate --fake-initial
```

5. Start the dev server:

```bash
python manage.py runserver
```

## Production Deployment

### Static and Media

- Static files are served with WhiteNoise
- `STATIC_ROOT` is `staticfiles/`
- collect static with:

```bash
python manage.py collectstatic --noinput
```

- Media uploads are stored in `media/` locally
- For production, use object storage instead of local disk

### Gunicorn

The repo includes:

- `Procfile`
- `build.sh`
- `render.yaml`

Gunicorn command:

```bash
gunicorn omegaerp.wsgi:application --log-file -
```

### Production Checklist

- Set `DJANGO_SETTINGS_MODULE=omegaerp.settings.production`
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Configure `CSRF_TRUSTED_ORIGINS`
- Use a production PostgreSQL database
- Run `python manage.py collectstatic --noinput`
- Run `python manage.py migrate --noinput`
- Serve behind HTTPS

## GitHub Setup

Repository URL:

```text
https://github.com/Techfirst123/OmegaCRM.git
```

Git commands:

```bash
git init
git add .
git commit -m "Initial OmegaERP commit"
git branch -M main
git remote add origin https://github.com/Techfirst123/OmegaCRM.git
git push -u origin main
```

## Production Architecture Recommendation

Recommended architecture for this Django-heavy project:

- Frontend: keep Django templates in the same backend service for now
- Backend: deploy Django + Gunicorn on a persistent Python service
- PostgreSQL: managed Postgres
- Media storage: object storage such as S3-compatible storage

Practical recommendation:

- Backend: Render Web Service or Railway service
- Database: Render PostgreSQL or Neon PostgreSQL
- Media: AWS S3 or Cloudflare R2

The repository includes a starter `render.yaml` for the Render path. Update the hostname values before using it.

This project is not a strong fit for a Vercel-first deployment because the current app is server-rendered Django with database-backed workflows and uploaded files, rather than a lightweight stateless frontend plus serverless API.

## Security Notes

The production settings enable or support:

- `SECURE_SSL_REDIRECT`
- secure session cookies
- secure CSRF cookies
- HSTS
- `SECURE_CONTENT_TYPE_NOSNIFF`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_PROXY_SSL_HEADER`

Before production launch:

- replace the local `.env` secret key
- verify all API keys live only in `.env`
- verify `DEBUG=False`
- use HTTPS only
- move user-uploaded files to object storage

## Files Added for Deployment

- `.env.example`
- `Procfile`
- `build.sh`
- `render.yaml`
- `omegaerp/settings/base.py`
- `omegaerp/settings/development.py`
- `omegaerp/settings/production.py`
- `staticfiles/.gitkeep`

## Notes

- `vercel.json` was intentionally not added because Vercel is not the recommended primary deployment target for this backend-heavy Django application.
- Local user-uploaded files under `media/` were left in place but are excluded from Git.
