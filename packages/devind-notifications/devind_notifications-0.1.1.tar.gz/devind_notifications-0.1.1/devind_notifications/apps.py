from django.apps import AppConfig

from devind_helpers.redis_client import redis


class NotificationsConfig(AppConfig):
    name = 'devind_notifications'

    def ready(self):
        redis.delete('listening')
