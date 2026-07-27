import os
import json
from typing import List, Tuple

from django.conf import settings


def extract_text_from_pdf(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        texts = [p.extract_text() or '' for p in reader.pages]
        return '\n'.join(texts)
    except Exception:
        return ''


def extract_text_from_image(path: str) -> str:
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ''


def extract_text_from_excel(path: str) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        texts = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                texts.append(' '.join([str(c) for c in row if c is not None]))
        return '\n'.join(texts)
    except Exception:
        return ''


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    if ext in ('pdf',):
        return extract_text_from_pdf(path)
    if ext in ('png', 'jpg', 'jpeg', 'tiff', 'bmp'):
        return extract_text_from_image(path)
    if ext in ('xls', 'xlsx'):
        return extract_text_from_excel(path)
    # try plain text
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''


def build_faiss_index(vectors, ids: List[int], output_dir: str):
    import numpy as np
    import faiss
    os.makedirs(output_dir, exist_ok=True)
    np_vectors = np.vstack(vectors).astype('float32')
    dim = np_vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np_vectors)
    index_path = os.path.join(output_dir, 'faiss.index')
    faiss.write_index(index, index_path)

    mapping = {str(i): ids[i] for i in range(len(ids))}
    mapping_path = os.path.join(output_dir, 'mapping.json')
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f)

    return index_path, mapping_path


def embed_texts(model_name: str, texts: List[str], batch_size: int = 32):
    from sentence_transformers import SentenceTransformer
    import numpy as np

    print("\n===== SAMPLE TEXTS BEING EMBEDDED =====")
    for t in texts[:5]:
        print(t)
    print("=====================================\n")

    model = SentenceTransformer(model_name)

    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        emb = model.encode(batch, convert_to_numpy=True)
        vectors.append(emb.astype('float32'))

    if vectors:
        return np.vstack(vectors)

    return None

def ingest_directory(base_path: str, output_dir: str, model_name: str = 'all-MiniLM-L6-v2', batch_size: int = 32, skip_existing: bool = True):
    """Walk `base_path`, extract text, create Document rows and build a FAISS index.

    Returns: (num_indexed, index_path, mapping_path)
    """
    from .models import Document
    texts = []
    ids = []
    doc_objects = []

    base_path = os.path.abspath(base_path)
    for root, dirs, files in os.walk(base_path):
        for fname in files:
            path = os.path.join(root, fname)
            text = extract_text(path)
            if not text:
                continue

            if skip_existing and Document.objects.filter(file_path=path).exists():
                continue

            doc = Document.objects.create(title=fname, file_path=path, content=text)
            doc_objects.append(doc)
            texts.append(text)
            ids.append(doc.id)

    if not texts:
        return 0, None, None

    vecs = embed_texts(model_name, texts, batch_size=batch_size)
    if vecs is None:
        return 0, None, None

    # Save embeddings into Document.embedding when available (Postgres + pgvector)
    for doc, vec in zip(doc_objects, vecs):
        try:
            # VectorField expects a list
            doc.embedding = list(map(float, vec.tolist()))
            doc.save(update_fields=['embedding'])
        except Exception:
            # ignore if DB doesn't support vector field
            pass

    vectors = [vec for vec in vecs]
    index_path, mapping_path = build_faiss_index(vectors, ids, output_dir)
    return len(ids), index_path, mapping_path
