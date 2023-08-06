import graphene

from .notification_subscription import NotificationsSubscription


class NotificationSubscriptions(graphene.ObjectType):
    notifications = NotificationsSubscription.Field(required=True, description='Поток новых уведомлений')
