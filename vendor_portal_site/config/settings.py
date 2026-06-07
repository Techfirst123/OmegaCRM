from pathlib import Path
import os
from urllib.parse import urlparse

import environ


BASE_DIR = Path(__file__).resolve().parent.parent
ERP_ROOT = BASE_DIR.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'vendor-portal-dev-secret'),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
)
environ.Env.read_env(ERP_ROOT / '.env')

SECRET_KEY = env('VENDOR_PORTAL_SECRET_KEY', default=env('SECRET_KEY'))
DEBUG = env.bool('VENDOR_PORTAL_DEBUG', default=True)
ERP_API_BASE_URL = env('ERP_API_BASE_URL', default='http://127.0.0.1:8000/api/vendor-portal')
PORTAL_BRAND_NAME = env('VENDOR_PORTAL_BRAND_NAME', default='Omega Vendor Portal')
PORTAL_APP_SUBTITLE = env('VENDOR_PORTAL_APP_SUBTITLE', default='Standalone field reporting')
PORTAL_SUPPORT_EMAIL = env('VENDOR_PORTAL_SUPPORT_EMAIL', default='support@omega-group.local')
PORTAL_PUBLIC_URL = env('VENDOR_PORTAL_PUBLIC_URL', default='http://127.0.0.1:8001')
PORTAL_PRIMARY_COLOR = env('VENDOR_PORTAL_PRIMARY_COLOR', default='#0d5cab')
PORTAL_REFRESH_THRESHOLD_SECONDS = env.int('VENDOR_PORTAL_REFRESH_THRESHOLD_SECONDS', default=60 * 30)
ALLOWED_HOSTS = env.list('VENDOR_PORTAL_ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])
portal_public_host = urlparse(PORTAL_PUBLIC_URL).hostname or ''
for host in ['.vercel.app', '.onrender.com', portal_public_host, os.environ.get('VERCEL_URL', '')]:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
CSRF_TRUSTED_ORIGINS = env.list('VENDOR_PORTAL_CSRF_TRUSTED_ORIGINS', default=[])
for origin in [
    'https://*.vercel.app',
    'https://*.onrender.com',
    f'https://{portal_public_host}' if portal_public_host else '',
    f"https://{os.environ.get('VERCEL_URL', '')}" if os.environ.get('VERCEL_URL') else '',
]:
    if origin and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'portal.context_processors.portal_branding',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'portal.sqlite3',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Calcutta'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

USE_X_FORWARDED_HOST = env.bool('VENDOR_PORTAL_USE_X_FORWARDED_HOST', default=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
