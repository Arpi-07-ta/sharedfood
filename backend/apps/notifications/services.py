from apps.accounts.models import User

from .models import Notification


def create_notification(*, recipient, title, message, event_code, notification_type=Notification.NotificationType.INFO, donation=None, action_url=''):
    if not recipient or not recipient.is_active:
        return None
    return Notification.objects.create(
        recipient=recipient,
        title=title[:255],
        message=message,
        event_code=event_code[:60],
        notification_type=notification_type,
        related_donation=donation,
        action_url=action_url[:500],
    )


def notify_admins(*, title, message, event_code, notification_type=Notification.NotificationType.ALERT, donation=None, action_url=''):
    return [
        create_notification(
            recipient=admin,
            title=title,
            message=message,
            event_code=event_code,
            notification_type=notification_type,
            donation=donation,
            action_url=action_url,
        )
        for admin in User.objects.filter(role=User.Role.ADMIN, is_active=True)
    ]
