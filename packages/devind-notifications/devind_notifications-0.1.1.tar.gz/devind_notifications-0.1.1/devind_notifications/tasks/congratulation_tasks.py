from datetime import date
from typing import Optional, Type

from celery import shared_task

from apps.core.models import User
from devind_notifications.models import AbstractNotice, get_notice_model
from .notification_tasks import send_notification

Notice: Type[AbstractNotice] = get_notice_model()


@shared_task
def happy_birthday():
    """Поздравление с днем рождения."""
    for user in User.objects.all():
        notice: Optional[Notice] = None
        if user.birthday == date.today():
            notice = Notice.objects.create(kind=Notice.HAPPY_BIRTHDAY) if notice is None else notice
            notice.notification_set.create(user=user)
            send_notification.delay(notice.id)
