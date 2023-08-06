from typing import Optional

import graphene
from graphql_relay import to_global_id

from devind_core.schema.subscriptions import BaseSubscription
from devind_helpers.schema.types import ConsumerActionType
from devind_helpers.decorators import register_users
from devind_helpers.orm_utils import get_object_or_none
from devind_notifications.models import Notification
from ..types import NotificationType


class NotificationsSubscription(BaseSubscription):
    """Подписка на обновление событий."""
    notification = graphene.Field(NotificationType)

    @staticmethod
    @register_users('listening')
    def subscribe(root, info, *args, **kwargs):
        """Добавляем в группу пользователя
        :param root:
        :param info:
        :return:
        """
        user_id = info.context.user.id if hasattr(info.context, 'user') else None
        return f'notification.{user_id}',

    @staticmethod
    @register_users('listening', True)
    def unsubscribed(root, info, *args, **kwargs):
        pass

    @staticmethod
    def publish(payload: dict, info, *args, **kwargs):
        action: ConsumerActionType = payload.get('action_value', ConsumerActionType.ADD)
        object_id: Optional[int] = payload.get('object_id', None)
        nf_id: str = to_global_id(str(NotificationType), object_id)
        if action == ConsumerActionType.DELETE:
            return NotificationsSubscription(action=action, id=nf_id)
        notification: Optional[Notification] = get_object_or_none(Notification, pk=object_id)
        if notification is None:
            return NotificationsSubscription.SKIP
        return NotificationsSubscription(action=action, id=nf_id, notification=notification)
