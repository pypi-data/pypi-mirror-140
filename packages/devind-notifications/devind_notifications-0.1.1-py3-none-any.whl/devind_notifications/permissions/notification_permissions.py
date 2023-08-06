from devind_helpers.permissions import BasePermission
from devind_notifications.models import Notification


class ChangeNotification(BasePermission):
    """Пропускает пользователей, которые могут изменять оповещение пользователей"""

    @staticmethod
    def has_object_permission(context, notification: Notification):
        return context.user.has_perm('devind_notifications.change_notification') or context.user == notification.user


class DeleteNotification(BasePermission):
    """Пропускает пользователей, которые могут удалять оповещение пользователей"""

    @staticmethod
    def has_object_permission(context, notification: Notification):
        return context.user.has_perm('devind_notifications.delete_notification') or context.user == notification.user
