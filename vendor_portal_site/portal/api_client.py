import json
import mimetypes
import uuid
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class PortalApiError(Exception):
    pass


def _build_url(path):
    base = settings.ERP_API_BASE_URL.rstrip('/') + '/'
    return urljoin(base, path.lstrip('/'))


def _headers(token=None):
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def _handle_response(response):
    try:
        payload = json.loads(response.read().decode('utf-8'))
    except Exception as exc:
        raise PortalApiError('Vendor portal API returned an invalid response.') from exc
    if response.status >= 400 or not payload.get('ok', False):
        raise PortalApiError(payload.get('error') or 'Vendor portal API request failed.')
    return payload


def _post_body(data=None, files=None):
    if not files:
        encoded = urlencode(data or {}).encode('utf-8')
        return encoded, 'application/x-www-form-urlencoded'

    boundary = f'----VendorPortalBoundary{uuid.uuid4().hex}'
    chunks = []
    for key, value in (data or {}).items():
        chunks.extend([
            f'--{boundary}\r\n'.encode('utf-8'),
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'),
            str(value).encode('utf-8'),
            b'\r\n',
        ])

    for key, uploaded in (files or {}).items():
        filename = getattr(uploaded, 'name', 'upload.bin')
        content = uploaded.read()
        content_type = getattr(uploaded, 'content_type', '') or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        chunks.extend([
            f'--{boundary}\r\n'.encode('utf-8'),
            f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode('utf-8'),
            f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'),
            content,
            b'\r\n',
        ])
    chunks.append(f'--{boundary}--\r\n'.encode('utf-8'))
    return b''.join(chunks), f'multipart/form-data; boundary={boundary}'


def post(path, *, data=None, files=None, token=None):
    body, content_type = _post_body(data=data, files=files)
    headers = _headers(token)
    headers['Content-Type'] = content_type
    request = Request(_build_url(path), data=body, headers=headers, method='POST')
    try:
        with urlopen(request, timeout=30) as response:
            return _handle_response(response)
    except HTTPError as exc:
        return _handle_response(exc)
    except URLError as exc:
        raise PortalApiError('Could not connect to the OmegaERP API service.') from exc


def get(path, *, params=None, token=None):
    query = urlencode(params or {})
    url = _build_url(path)
    if query:
        url = f'{url}?{query}'
    request = Request(url, headers=_headers(token), method='GET')
    try:
        with urlopen(request, timeout=30) as response:
            return _handle_response(response)
    except HTTPError as exc:
        return _handle_response(exc)
    except URLError as exc:
        raise PortalApiError('Could not connect to the OmegaERP API service.') from exc


def refresh_token(token):
    return post('auth/refresh/', token=token, data={})
