from django.urls import path

from .views import (
	MarkAllNotificationsReadView,
	MarkNotificationReadView,
	NotificationListView,
	UnreadNotificationCountView,
)

urlpatterns = [
	path('', NotificationListView.as_view(), name='notification-list'),
	path('unread-count/', UnreadNotificationCountView.as_view(), name='notification-unread-count'),
	path('read-all/', MarkAllNotificationsReadView.as_view(), name='notification-read-all'),
	path('<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='notification-read'),
]
