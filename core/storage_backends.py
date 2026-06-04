from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage
from django.http import FileResponse
from django.urls import reverse
from vercel.blob import BlobClient, get, head


class VercelPrivateMediaStorage(Storage):
    def __init__(self):
        self.client = BlobClient(token=settings.BLOB_READ_WRITE_TOKEN)
        self.access = settings.VERCEL_BLOB_ACCESS

    def _open(self, name, mode='rb'):
        blob = get(name, access=self.access, token=settings.BLOB_READ_WRITE_TOKEN)
        content = ContentFile(blob.content)
        content.name = name
        return File(content, name=name)

    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        blob = self.client.put(
            name,
            content.read(),
            access=self.access,
            content_type=getattr(content, 'content_type', None),
            add_random_suffix=True,
        )
        return blob.pathname

    def delete(self, name):
        if name:
            self.client.delete(name)

    def exists(self, name):
        return False

    def size(self, name):
        return head(name, token=settings.BLOB_READ_WRITE_TOKEN).size

    def url(self, name):
        return reverse('media-blob-proxy', kwargs={'blob_path': name})

    def get_available_name(self, name, max_length=None):
        return name if max_length is None else name[:max_length]

    def path(self, name):
        raise NotImplementedError('Vercel Blob storage does not provide a local filesystem path.')

    def listdir(self, path):
        return [], []


def build_blob_download_response(blob_path):
    blob = get(blob_path, access=settings.VERCEL_BLOB_ACCESS, token=settings.BLOB_READ_WRITE_TOKEN)
    buffer = BytesIO(blob.content)
    response = FileResponse(buffer, content_type=blob.content_type or 'application/octet-stream')
    response['Content-Disposition'] = blob.content_disposition
    response['Content-Length'] = str(blob.size or len(blob.content))
    return response
