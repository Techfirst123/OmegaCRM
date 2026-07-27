from django.db import models
try:
    from pgvector.fields import VectorField
except Exception:
    VectorField = None


class Document(models.Model):
    title = models.CharField(max_length=500, blank=True)
    file_path = models.CharField(max_length=2000, unique=True)
    content = models.TextField(blank=True)
    if VectorField is not None:
        embedding = VectorField(dim=384, null=True, blank=True)
    else:
        embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.file_path


class ExistingDocument(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    document_type = models.TextField(blank=True, null=True)
    vendor_name = models.TextField(blank=True, null=True)
    po_number = models.TextField(blank=True, null=True)
    invoice_number = models.TextField(blank=True, null=True)
    project_name = models.TextField(blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)

    if VectorField:
        embedding = VectorField(dimensions=384, null=True, blank=True)
    class Meta:
        db_table = 'search_document'
        managed = False

    def __str__(self):
        return self.title or f'doc-{self.id}'
