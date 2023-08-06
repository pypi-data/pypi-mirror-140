from typing import Optional, Iterable

import graphene
from django.db.models.fields import BooleanField
from graphql import ResolveInfo
from graphql_relay import from_global_id

from devind_helpers.schema.types import ErrorFieldType, ConsumerActionType
from devind_helpers.decorators import permission_classes
from devind_helpers.orm_utils import get_object_or_none
from devind_helpers.permissions import IsAuthenticated
from devind_helpers.schema.mutations import BaseMutation
from devind_notifications.models import Notification
from devind_notifications.permissions import DeleteNotification
from devind_notifications.schema.subscriptions import NotificationsSubscription


class ChangeNotificationMutation(BaseMutation):
    """Изменение уведомления"""

    class Input:
        notification_id = graphene.ID(required=True, description='Идентификатор уведомления')
        field = graphene.String(required=True, description='Название поля')
        value = graphene.Boolean(required=True, description='Значение')

    @staticmethod
    @permission_classes([IsAuthenticated, DeleteNotification])
    def mutate_and_get_payload(root, info: ResolveInfo, notification_id: str, field: str, value: bool, **kwargs):
        notification: Optional[Notification] = get_object_or_none(Notification, pk=from_global_id(notification_id)[1])
        if notification is None:
            return ChangeNotificationMutation(
                success=False,
                errors=[ErrorFieldType(field, [f'Уведомление с идентификатором {notification_id} не найдено.'])]
            )
        info.context.check_object_permissions(info.context, notification)
        if not hasattr(notification, field) or not isinstance(getattr(notification, field), bool):
            return ChangeNotificationMutation(
                success=False,
                errors=[ErrorFieldType(field, [f'Поле {field} не обнаружено'])]
            )
        setattr(notification, field, value)
        notification.save(update_fields=(field,))
        NotificationsSubscription.notify(
            f'notification.{notification.user_id}',
            ConsumerActionType.DELETE if field == 'hide' else ConsumerActionType.CHANGE,
            notification.id
        )
        return ChangeNotificationMutation()


class ChangeNotificationsMutation(BaseMutation):
    """Изменение всех уведомлений"""

    class Input:
        notifications_id = graphene.List(graphene.ID, required=True, description='Идентификаторы уведомлений')
        field = graphene.String(required=True, description='Название поля')
        value = graphene.Boolean(required=True, description='Значение')

    @staticmethod
    @permission_classes([IsAuthenticated, DeleteNotification])
    def mutate_and_get_payload(root, info: ResolveInfo, notifications_id: list[str], field: str, value: bool, **kwargs):
        notifications_id = [from_global_id(nid)[1] for nid in notifications_id]
        if not hasattr(Notification, field) or not isinstance(getattr(Notification, field).field, BooleanField):
            return ChangeNotificationsMutation(
                success=False,
                errors=[ErrorFieldType(field, [f'Поле {field} не обнаружено'])]
            )
        notifications: Iterable[Notification] = Notification.objects.filter(pk__in=notifications_id)
        for notification in notifications:
            info.context.check_object_permissions(info.context, notification)
            setattr(notification, field, value)
            notification.save(update_fields=(field,))
            NotificationsSubscription.notify(
                f'notification.{notification.user_id}',
                ConsumerActionType.DELETE if field == 'hide' else ConsumerActionType.CHANGE,
                notification.id
            )
        return ChangeNotificationsMutation()
