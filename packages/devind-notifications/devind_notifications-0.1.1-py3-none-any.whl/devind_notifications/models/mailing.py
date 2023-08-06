import importlib

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


def default_dispatchers() -> list[str]:
    """Получение отправителей уведомлений по умолчанию.

    :return: названия классов отправителей уведомлений по умолчанию
    """

    return list(['EmailDispatch'])


def mailing_default_email(instance) -> str:
    """Получение email по умолчанию

    :param instance: оповещение
    :return: email по умолчанию
    """

    return instance.user.email


def attachments_directory_path(instance, filename: str) -> str:
    """Получение пути к директории с прикрепленными файлами (ma - mailing attachments).

    :param instance: оповещение
    :param filename: название файла
    :return: путь к директории с прикрепленными файлами
    """

    return f'storage/ma/{instance.user.id}/{filename}'


class AbstractMailing(models.Model):
    """Оповещение

    dispatchers
        - EmailDispatch - отправка по средствам электронной почты
        - TelegramDispatch - отправка по средства телеграмма
    """

    dispatchers = ArrayField(
        models.CharField(max_length=30),
        default=default_dispatchers,
        help_text='Средства отправки'
    )
    address = models.EmailField(default=mailing_default_email, help_text='Адрес отправки')
    header = models.CharField(max_length=256, help_text='Заголовок сообщения')
    text = models.TextField(help_text='Текст сообщения')
    attachments = ArrayField(
        models.FileField(upload_to=attachments_directory_path, max_length=1024, help_text='Файлы'),
        help_text='Массив прикрепленных файлов',
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text='Дата добавления')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Пользователь')

    class Meta:
        abstract = True

    def dispatch(self, notify: bool = False) -> None:
        """Отправка оповещения.

        :param notify: отправлять ли уведомление
        """
        # from devind_notifications.models import get_notice_model
        # Notice: Type[models.Model] = get_notice_model() # noqa

        from . import Notice
        from devind_notifications.tasks import send_notification

        dispatch_module = importlib.import_module('devind_notifications.helpers.dispatch')
        dispatchers = [dispatch for dispatch in self.dispatchers if hasattr(dispatch_module, dispatch)]
        for dispatch in dispatchers:
            getattr(dispatch_module, dispatch)(self).send()
        if notify:
            notice: Notice = Notice.objects.create(
                kind=Notice.MAILING,
                payload=self.header,
                object_id=self.pk,
                user=self.user
            )
            notice.notification_set.create(user=self.user)
            send_notification.delay(notice_id=notice.pk)
            # runner_task: str = 'devind_notifications.tasks.notification_tasks.send_notification'
            # current_app.tasks[runner_task].delay(notice_id=notice.pk)
