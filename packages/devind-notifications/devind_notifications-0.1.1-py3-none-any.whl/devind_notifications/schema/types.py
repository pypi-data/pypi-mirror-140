import graphene
from django.utils.module_loading import import_string
from graphene.relay import Node
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from devind_core.schema.connections.countable_connection import CountableConnection
from devind_core.schema.types import OptimizedDjangoObjectType
from devind_core.settings import devind_settings
from devind_helpers.orm_utils import get_object_or_none
from ..models import Notice, Notification, Mailing
from ..settings import notifications_settings

NoticeInterface = import_string(notifications_settings.NOTICE_INTERFACE)


class NoticeType(OptimizedDjangoObjectType):
    """Уведомление"""

    user = graphene.Field(devind_settings.USER_TYPE, description='Пользователь')

    class Meta:
        model = Notice
        interfaces = (Node,)
        fields = ('id', 'kind', 'payload', 'object_id', 'created_at', 'user',)
        filter_fields = {
            'user': ['exact']
        }
        connection_class = CountableConnection


class NoticeEmptyType(graphene.ObjectType):
    """Уведомление без дополнительного содержимого"""

    class Meta:
        model = Notice
        interfaces = (NoticeInterface,)
        fields = ('id', 'kind', 'payload', 'object_id', 'created_at', 'user',)


class NoticeMailingType(graphene.ObjectType):
    """Уведомление типа 'Пришло уведомление'."""

    mailing = graphene.Field(lambda: MailingType, description='Оповещение пользователя')

    class Meta:
        model = Notice
        interfaces = (NoticeInterface,)
        fields = ('id', 'kind', 'payload', 'object_id', 'created_at', 'user', 'mailing',)

    @staticmethod
    def resolve_mailing(notice: Notice, info: ResolveInfo, *args, **kwargs):
        return get_object_or_none(Mailing, pk=notice.object_id)


class NotificationType(DjangoObjectType):
    """Оповещение пользователей"""

    user = graphene.Field(notifications_settings.USER_TYPE, required=True, description='Пользователь')
    notice = graphene.Field(notifications_settings.NOTICE_INTERFACE, required=True, description='Уведомление')

    class Meta:
        model = Notification
        interfaces = (Node,)
        fields = ('id', 'read', 'hide', 'created_at', 'user', 'notice',)
        filter_fields = {
            'user': ['exact'],
            'notice': ['exact'],
            'hide': ['exact'],
        }
        connection_class = CountableConnection


class MailingType(DjangoObjectType):
    """Оповещение"""

    user = graphene.Field(notifications_settings.USER_TYPE, required=True, description='Пользователь')

    class Meta:
        model = Mailing
        fields = ('id', 'dispatchers', 'address', 'header', 'text', 'attachments', 'created_at', 'user',)
