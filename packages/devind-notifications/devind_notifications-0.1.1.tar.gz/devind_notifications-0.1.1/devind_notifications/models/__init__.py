"""Модуль получения абстрактных моделей, содержащихся в уведомлениях приложения."""

from typing import Type

from django.apps import apps

from .mailing import AbstractMailing
from .notification import AbstractNotice, AbstractNotification
from ..settings import notifications_settings


class Notice(AbstractNotice):
    """Модель хранения уведомлений."""

    class Meta(AbstractNotice.Meta):
        """Мета-класс модели хранения уведомлений."""
        pass


def get_notice_model() -> Type[AbstractNotice]:
    """Функция получения модели хранения уведомлений."""
    return apps.get_model(notifications_settings.NOTICE_MODEL)


class Notification(AbstractNotification):
    """Модель хранения рассылаемых уведомлений."""

    class Meta(AbstractNotification.Meta):
        """Мета-класс хранения рассылаемых уведомлений."""
        pass


def get_notification_model() -> Type[AbstractNotification]:
    """Функция получения модель хранения рассылок уведомлений."""
    return apps.get_model(notifications_settings.NOTIFICATION_MODEL)


class Mailing(AbstractMailing):
    """Модель хранения отправленных электронных писем."""

    class Meta(AbstractMailing.Meta):
        """Мета-класс хранения отправленных электронных писем."""
        pass


def get_mailing_model() -> Type[AbstractMailing]:
    """Функция получения модели отправленных электронных писем."""
    return apps.get_model(notifications_settings.MAILING_MODEL)
