def serialize_document(document):
    return {
        'id': document.id,
        'document_type': document.document_type,
        'title': document.title,
        'file_url': document.file.url if document.file else '',
        'created_at': document.created_at.isoformat() if document.created_at else '',
    }
