from django.core.management.base import BaseCommand
from django.conf import settings
from search import indexer
from search.models import Document
import os
from typing import List, Tuple


def build_rich_text(fields: dict, skip_keys: set = None) -> str:
    """Combine all text-ish field values into one rich text block for embedding."""
    if skip_keys is None:
        skip_keys = {'id', 'created_at', 'updated_at', 'embedding', 'is_active', 'display_order'}
    parts = []
    for key, val in fields.items():
        if key in skip_keys:
            continue
        if val is None or str(val).strip() in ('', 'None', '0', 'False'):
            continue
        label = key.replace('_', ' ').replace(' id', '').strip()
        parts.append(f'{label}: {val}')
    return ' | '.join(parts)


def extract_rows(cursor, table: str) -> List[dict]:
    cursor.execute(f"SELECT * FROM \"{table}\" ORDER BY id")
    cols = [desc[0] for desc in cursor.description]
    rows = []
    for row in cursor.fetchall():
        rows.append(dict(zip(cols, row)))
    return rows


TABLE_IMPORTS = [
    {
        'table': 'material_master',
        'title_field': 'material_name',
        'fallback_title': lambda r: r.get('material_code') or f"MAT-{r['id']}",
    },
    {
        'table': 'vendor_registration',
        'title_field': 'company_name',
        'fallback_title': lambda r: f"Vendor-{r['id']}",
    },
    {
        'table': 'project_master',
        'title_field': 'project_name',
        'fallback_title': lambda r: f"Project-{r['id']}",
    },
    {
        'table': 'purchase_orders_purchaseorder',
        'title_field': 'po_number',
        'fallback_title': lambda r: f"PO-{r['id']}",
    },
    {
        'table': 'purchase_orders_purchaseorderitem',
        'title_field': 'material_name',
        'fallback_title': lambda r: f"POItem-{r['id']}",
    },
    {
        'table': 'purchase_orders_purchaseorderreferencecode',
        'title_field': 'reference_code',
        'fallback_title': lambda r: f"RefCode-{r['id']}",
    },
    {
        'table': 'project_work_allocation',
        'title_field': None,
        'fallback_title': lambda r: f"Allocation-{r['id']}",
    },
    {
        'table': 'work_packages',
        'title_field': 'name',
        'fallback_title': lambda r: f"WP-{r['id']}",
    },
    {
        'table': 'business_units',
        'title_field': 'name',
        'fallback_title': lambda r: f"BU-{r['id']}",
    },
    {
        'table': 'master_data_entries',
        'title_field': 'name',
        'fallback_title': lambda r: f"MDE-{r['id']}",
    },
    {
        'table': 'staff_profiles',
        'title_field': 'staff_name',
        'fallback_title': lambda r: f"Staff-{r['id']}",
    },
    {
        'table': 'vendor_portal_project_assignments',
        'title_field': 'site_name',
        'fallback_title': lambda r: f"Assignment-{r['id']}",
    },
    {
        'table': 'vendor_tasks',
        'title_field': 'task_title',
        'fallback_title': lambda r: f"Task-{r['id']}",
    },
    {
        'table': 'vendor_assignments',
        'title_field': None,
        'fallback_title': lambda r: f"VendorAssignment-{r['id']}",
    },
]


class Command(BaseCommand):
    help = 'Import documents from ALL DB tables into search.Document, embed and build FAISS index.'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', default=os.path.join(settings.BASE_DIR, 'vector_index'))
        parser.add_argument('--model', default='all-MiniLM-L6-v2')
        parser.add_argument('--batch-size', type=int, default=32)
        parser.add_argument('--skip-existing', action='store_true', default=True)
        parser.add_argument('--reindex', action='store_true', help='Clear all existing documents and rebuild from scratch')
        parser.add_argument('--source', choices=['document_index', 'material_master', 'all'], default='all')

    def handle(self, *args, **options):
        output = options['output']
        model = options['model']
        batch_size = options['batch_size']
        skip_existing = options['skip_existing']
        source = options.get('source') or 'all'

        if options.get('reindex'):
            self.stdout.write('Clearing all existing documents...')
            Document.objects.all().delete()
            import shutil
            if os.path.exists(output):
                shutil.rmtree(output)
            skip_existing = False

        from django.db import connection

        texts: List[str] = []
        ids: List[int] = []
        created: List[Document] = []

        if source == 'document_index':
            self._import_document_index(connection, texts, ids, created, skip_existing)
        elif source == 'material_master':
            self._import_table(connection, 'material_master', TABLE_IMPORTS[0], texts, ids, created, skip_existing)
        else:
            for cfg in TABLE_IMPORTS:
                self._import_table(connection, cfg['table'], cfg, texts, ids, created, skip_existing)

        if not texts:
            self.stdout.write(self.style.WARNING('No new documents to import.'))
            return

        self.stdout.write(f'Embedding {len(texts)} documents using {model}...')
        vecs = indexer.embed_texts(model, texts, batch_size=batch_size)
        if vecs is None:
            self.stdout.write(self.style.ERROR('Failed to compute embeddings.'))
            return

        self.stdout.write('Saving embeddings to DB...')
        for doc, vec in zip(created, vecs):
            try:
                doc.embedding = list(map(float, vec.tolist()))
                doc.save(update_fields=['embedding'])
            except Exception:
                pass

        os.makedirs(output, exist_ok=True)
        self.stdout.write('Building FAISS index...')
        index_path, mapping_path = indexer.build_faiss_index([v for v in vecs], ids, output)
        self.stdout.write(self.style.SUCCESS(f'Imported {len(ids)} documents.'))
        self.stdout.write(self.style.SUCCESS(f'Index: {index_path}'))
        self.stdout.write(self.style.SUCCESS(f'Mapping: {mapping_path}'))

    def _import_document_index(self, connection, texts, ids, created, skip_existing):
        from search.models import ExistingDocument
        qs = ExistingDocument.objects.all().order_by('id')
        for doc in qs:
            path = f'document_index:{doc.id}'
            if skip_existing and Document.objects.filter(file_path=path).exists():
                continue
            title = doc.title or f'doc-{doc.id}'
            d = Document.objects.create(title=title, file_path=path, content=doc.extracted_text or '')
            created.append(d)
            texts.append(doc.extracted_text if doc.extracted_text else title)
            ids.append(d.id)

    def _import_table(self, connection, table: str, cfg: dict, texts, ids, created, skip_existing):
        try:
            rows = extract_rows(connection.cursor(), table)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Skipping {table}: {e}'))
            return
        if not rows:
            self.stdout.write(f'  {table}: 0 rows, skipped')
            return

        imported = 0
        title_field = cfg['title_field']
        fallback = cfg['fallback_title']
        for row in rows:
            pk = row['id']
            path = f'{table}:{pk}'
            if skip_existing and Document.objects.filter(file_path=path).exists():
                continue
            title = row.get(title_field) if title_field else None
            if not title or str(title).strip() == '':
                title = fallback(row)
            content = build_rich_text(row)
            d = Document.objects.create(title=str(title).strip(), file_path=path, content=content)
            created.append(d)
            texts.append(content)
            ids.append(d.id)
            imported += 1

        self.stdout.write(f'  {table}: {len(rows)} rows, {imported} imported')
