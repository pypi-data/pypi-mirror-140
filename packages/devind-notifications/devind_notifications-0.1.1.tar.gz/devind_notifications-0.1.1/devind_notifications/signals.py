from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver([post_save], sender=Notification)
def handle_notification(sender, instance: Notification, **kwargs):
    """Логирование сохранения уведомления пользователей

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """

    pass
