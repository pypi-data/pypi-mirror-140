from django.conf import settings
from django.db import models

from ..settings import notifications_settings


class AbstractNotice(models.Model):
    """
    Абстрактная модель уведомлений.
        - INFO - Системное сообщение
        - PAGE - Добавлена новая страница
        - COMMENT - Добавлен комментарий
        - MESSAGE - Пришло сообщение
        - TASK - Выполнилась асинхронная задача
        - BILLING - Выставлен счет на оплату
        - PAID - Оплачено
        - MAILING - Пришло оповещение
        - HAPPY_BIRTHDAY - Поздравление с днем рождения
    """

    INFO = 0
    PAGE = 1
    COMMENT = 2
    MESSAGE = 3
    TASK = 4
    BILLING = 5
    PAID = 6
    MAILING = 7
    HAPPY_BIRTHDAY = 8

    KIND_NOTICE = (
        (INFO, 'info'),
        (PAGE, 'page'),
        (COMMENT, 'comment'),
        (MESSAGE, 'message'),
        (TASK, 'task'),
        (BILLING, 'billing'),
        (PAID, 'paid'),
        (MAILING, 'mailing'),
        (HAPPY_BIRTHDAY, 'happy_birthday')
    )

    kind = models.PositiveIntegerField(choices=KIND_NOTICE, default=PAGE, help_text='Тип уведомления')
    payload = models.CharField(max_length=1024, help_text='Полезная нагрузка')
    object_id = models.CharField(max_length=100, help_text='Идентификатор объекта')

    created_at = models.DateTimeField(auto_now_add=True, help_text='Дата добавления')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, help_text='Пользователь')

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class AbstractNotification(models.Model):
    """Абстрактная модель оповещения пользователей."""

    read = models.BooleanField(default=False, help_text='Прочитано ли уведомление')
    hide = models.BooleanField(default=False, help_text='Скрыть уведомление')

    created_at = models.DateTimeField(auto_now_add=True, help_text='Дата добавления')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Пользователь')
    notice = models.ForeignKey(notifications_settings.NOTICE_MODEL, on_delete=models.CASCADE, help_text='Уведомление')

    class Meta:
        abstract = True
        ordering = ('-created_at',)
