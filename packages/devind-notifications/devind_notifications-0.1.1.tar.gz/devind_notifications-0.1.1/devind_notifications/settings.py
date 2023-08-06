"""
Этот модуль представляет собой набор настреок для реализации уведомлений.
"""

from typing import Optional, Dict

from django.conf import settings

USER_TYPE = getattr(settings, 'DEVIND_CORE_USER_TYPE', 'devind_core.schema.UserType')

MAILING_MODEL = getattr(settings, 'DEVIND_NOTIFICATION_MAILING_MODEL', 'devind_notifications.Mailing')
NOTICE_MODEL = getattr(settings, 'DEVIND_NOTIFICATION_NOTICE_MODEL', 'devind_notifications.Notice')
NOTIFICATION_MODEL = getattr(settings, 'DEVIND_NOTIFICATION_NOTIFICATION_MODEL', 'devind_notifications.Notification')
NOTICE_INTERFACE = getattr(
    settings,
    'DEVIND_NOTIFICATION_NOTICE_INTERFACE',
    'devind_notifications.schema.types.NoticeInterface'
)


DEFAULTS = {
    'USER_TYPE': USER_TYPE,
    'MAILING_MODEL': MAILING_MODEL,
    'NOTICE_MODEL': NOTICE_MODEL,
    'NOTIFICATION_MODEL': NOTIFICATION_MODEL,
    'NOTICE_INTERFACE': NOTICE_INTERFACE,
}


class DevindNotificationsSettings:
    """Настройки приложения devind_notifications."""

    def __init__(self, defaults: Optional[Dict] = None):
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, item: str) -> str:
        if item not in self.defaults:
            raise AttributeError(f'Invalid devind_notifications settings: {item}')
        return self.defaults[item]


notifications_settings = DevindNotificationsSettings(DEFAULTS)
