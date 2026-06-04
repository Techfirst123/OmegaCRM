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
- `BLOB_READ_WRITE_TOKEN`

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
- When `BLOB_READ_WRITE_TOKEN` is present, Django stores uploads in Vercel Blob instead of local disk
- This repository is configured to use a private Vercel Blob store for vendor documents in production

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

This project can be deployed to Vercel using Django support, but there are a couple of operational constraints to keep in mind:

- use a hosted PostgreSQL database, not local Postgres
- use object storage for user-uploaded media
- keep static files in the build via `collectstatic`

### Vercel Deployment

Vercel added zero-configuration Django support in April 2026, so this repository includes a small [vercel.json](C:/Users/lenovo/Desktop/slack/OmegaERP/vercel.json) only to make the static build step explicit.

Recommended Vercel environment variables:

```env
DJANGO_SETTINGS_MODULE=omegaerp.settings.production
SECRET_KEY=replace-with-a-long-random-value
DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_HOSTS=.vercel.app,your-production-domain.com
CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://your-production-domain.com
USE_X_FORWARDED_HOST=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Deploy steps:

1. Import the GitHub repository into Vercel.
2. Keep the detected framework as `Django`.
3. Add the production environment variables above.
4. Trigger the first deployment.
5. After deploy, set the exact Vercel hostname in `CSRF_TRUSTED_ORIGINS`.

If you need database schema changes, run them against the hosted PostgreSQL database before or immediately after the first production deploy.

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
