from devind_helpers.permissions import BasePermission, ModelPermission
from devind_notifications.models import Notice


AddNotice = ModelPermission('devind_notifications.add_notice')


class ChangeNotice(BasePermission):
    """Пропускает пользователей, которые могут изменять уведомление."""

    @staticmethod
    def has_object_permission(context, notice: Notice):
        """Непосредственная проверка разрешений."""
        return context.user.has_perm('devind_notifications.change_notice') or context.user == notice.user


class DeleteNotice(BasePermission):
    """Пропускает пользователей, которые могут удалять уведомление."""

    @staticmethod
    def has_object_permission(context, notice: Notice):
        """Непосредственная проверка разрешений."""
        return context.user.has_perm('devind_notifications.delete_notice') or context.user == notice.user
