from notifications.models import Notification


def create_notification(recipient, title, message, vendor=None, task=None, channel=Notification.CHANNEL_ERP):
    if not recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        vendor=vendor,
        task=task,
        title=title,
        message=message,
        channel=channel,
        status=Notification.STATUS_PENDING,
    )

