from functools import reduce
from typing import Optional, Iterable, Type

from celery import shared_task
from django.contrib.auth import get_user_model

from devind_core.models import Setting, SettingValue
from devind_helpers.schema.types import ConsumerActionType
from devind_helpers.orm_utils import get_object_or_none
from devind_helpers.utils import convert_str_to_bool
from devind_notifications.models import AbstractNotice, AbstractNotification, get_notice_model, get_notification_model
from devind_notifications.schema.subscriptions import NotificationsSubscription

User = get_user_model()
Notice: Type[AbstractNotice] = get_notice_model()
Notification: Type[AbstractNotification] = get_notification_model()


def get_ns(notice_id: int) -> tuple[Optional[Notice], Optional[Setting]]:
    """Получение показа уведомлений и настроек.

    :param notice_id: идентификатор уведомления
    :return: (показ уведомлений, настройки)
    """
    notice: Optional[Notice] = get_object_or_none(Notice, pk=notice_id)
    setting: Optional[Setting] = get_object_or_none(Setting, key='NOTIFICATION_PUSH')
    return notice, setting


@shared_task
def send_notification(notice_id: int) -> None:
    """Рассылка предзаполненного уведомления.

    :param notice_id: идентификатор уведомления
    """
    notice, setting = get_ns(notice_id)
    notifications: Iterable[Notification] = notice.notification_set.all()
    us = reduce(
        lambda a, c: {**a, **{c['user']: c['value']}},
        SettingValue.objects.filter(
            setting=setting,
            user_id__in=[n.user_id for n in notifications]
        ).values('user', 'value'),
        {}
    )
    for notification in notifications:
        if convert_str_to_bool(us.get(notification.user_id, setting.value)):
            NotificationsSubscription.notify(
                f'notification.{notification.user_id}',
                ConsumerActionType.ADD,
                notification.id
            )


@shared_task
def send_notifications(notice_id: int) -> None:
    """Рассылка предзаполненных уведомлений всем пользователям.

    :param notice_id: идентификатор уведомления
    """
    notice, setting = get_ns(notice_id)
    if not notice or not setting:
        return
    us = reduce(
        lambda a, c: {**a, **{c['user']: c['value']}},
        SettingValue.objects.filter(setting=setting).values('user', 'value'),
        {}
    )
    notifications = Notification.objects.bulk_create(
        [
            Notification(notice=notice, user_id=user_id)
            for user_id in User.objects.values_list('pk', flat=True)
            if convert_str_to_bool(us.get(user_id, setting.value))
        ]
    )
    for notification in notifications:
        NotificationsSubscription.notify(
            f'notification.{notification.user_id}',
            ConsumerActionType.ADD,
            notification.id
        )
