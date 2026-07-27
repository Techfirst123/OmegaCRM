import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
import os

from search import indexer


class Command(BaseCommand):
    help = 'Ingest documents from a directory and build FAISS index'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', default='documents')
        parser.add_argument('--output', '-o', default=os.path.join(settings.BASE_DIR, 'vector_index'))
        parser.add_argument('--model', default='all-MiniLM-L6-v2')
        parser.add_argument('--batch-size', type=int, default=32)
        parser.add_argument('--skip-existing', action='store_true', default=True)
        parser.add_argument('--reindex', action='store_true', help='Remove previous index and rebuild')

    def handle(self, *args, **options):
        base = options['path']
        base = os.path.abspath(base)
        output = options['output']
        model = options['model']
        batch_size = options['batch_size']
        skip_existing = options['skip_existing']

        if options.get('reindex') and os.path.exists(output):
            try:
                for fname in ('faiss.index', 'mapping.json'):
                    p = os.path.join(output, fname)
                    if os.path.exists(p):
                        os.remove(p)
            except Exception:
                pass

        os.makedirs(output, exist_ok=True)

        self.stdout.write(f'Ingesting from: {base}')
        num, index_path, mapping_path = indexer.ingest_directory(base, output_dir=output, model_name=model, batch_size=batch_size, skip_existing=skip_existing)

        if num:
            self.stdout.write(self.style.SUCCESS(f'Indexed {num} documents.'))
            self.stdout.write(self.style.SUCCESS(f'Index: {index_path}'))
            self.stdout.write(self.style.SUCCESS(f'Mapping: {mapping_path}'))
        else:
            self.stdout.write(self.style.WARNING('No documents were indexed.'))
