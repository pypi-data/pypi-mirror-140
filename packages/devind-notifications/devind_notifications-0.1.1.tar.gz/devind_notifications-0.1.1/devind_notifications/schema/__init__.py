import graphene
from django.db.models import QuerySet
from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo
from graphql_relay import from_global_id

from devind_helpers.decorators import permission_classes
from devind_helpers.orm_utils import get_object_or_404
from devind_helpers.permissions import IsAuthenticated
from .mutations import DeleteNoticeMutation, ChangeNotificationMutation, ChangeNotificationsMutation
from .subscriptions import NotificationSubscriptions
from .types import NoticeType, NoticeEmptyType, NoticeMailingType, NotificationType
from ..models import Notice, Notification


class Query(graphene.ObjectType):
    """Запросы приложения notifications."""

    notices = DjangoFilterConnectionField(NoticeType, required=True, description='Источник уведомлений')
    notifications = DjangoFilterConnectionField(NotificationType, required=True, description='Уведомления пользователя')
    notification = graphene.Field(
        NotificationType,
        notification_id=graphene.ID(required=True, description='Идентификатор уведомления'),
        required=True,
        description='Детализация уведомления'
    )

    @staticmethod
    @permission_classes([IsAuthenticated])
    def resolve_notices(root, info: ResolveInfo, *args, **kwargs) -> QuerySet:
        return Notice.objects.all()

    @staticmethod
    @permission_classes([IsAuthenticated])
    def resolve_notifications(root, info: ResolveInfo, *args, **kwargs) -> QuerySet:
        return Notification.objects.all()

    @staticmethod
    @permission_classes([IsAuthenticated])
    def resolve_notification(root, info: ResolveInfo, notification_id: str, *args, **kwargs) -> Notification:
        return get_object_or_404(Notification, pk=from_global_id(notification_id)[1])


class Mutation(graphene.ObjectType):
    """Мутации приложения notifications."""

    delete_notice = DeleteNoticeMutation.Field(required=True, description='Удаление уведомления')
    change_notification = ChangeNotificationMutation.Field(required=True, description='Изменение свойств уведомления')
    change_notifications = ChangeNotificationsMutation.Field(required=True, description='Изменение свойств уведомлений')


class Subscription(NotificationSubscriptions, graphene.ObjectType):
    """Подписки приложения notifications."""

    pass


types = [NoticeEmptyType, NoticeMailingType]
