import graphene
from graphene import Node
from graphql import ResolveInfo

from devind_core.settings import devind_settings
from devind_notifications.models import Notice


class NoticeInterface(Node):
    """Интерфейс уведомлений"""

    kind = graphene.Int(required=True, description='Тип уведомления')
    payload = graphene.String(required=True, description='Полезная нагрузка')
    object_id = graphene.String(required=True, description='Идентификатор объекта')
    created_at = graphene.DateTime(required=True, description='Дата создания')
    user = graphene.Field(devind_settings.USER_TYPE, description='Пользователь')

    class Meta:
        fields = ('id', 'kind', 'payload', 'object_id', 'created_at', 'user',)

    @classmethod
    def resolve_type(cls, notice: Notice, info: ResolveInfo):
        from devind_notifications.schema import NoticeEmptyType, NoticeMailingType
        resolver = {
            notice.INFO: NoticeEmptyType,
            notice.MAILING: NoticeMailingType,
            notice.HAPPY_BIRTHDAY: NoticeEmptyType,
        }
        return resolver.get(notice.kind, NoticeEmptyType)
