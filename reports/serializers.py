def serialize_saved_report(report):
    return {
        'id': report.id,
        'name': report.name,
        'report_type': report.report_type,
        'filters_json': report.filters_json,
        'created_at': report.created_at.isoformat() if report.created_at else '',
    }
