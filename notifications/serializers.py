from .models import Notification


def serialize_notification(entry: Notification):
    return {
        'id': entry.id,
        'title': entry.title,
        'message': entry.message,
        'channel': entry.channel,
        'status': entry.status,
        'created_at': entry.created_at.isoformat(),
    }

