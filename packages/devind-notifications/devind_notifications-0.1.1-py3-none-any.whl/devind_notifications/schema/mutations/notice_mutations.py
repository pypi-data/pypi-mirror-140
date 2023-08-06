import graphene
from graphql import ResolveInfo
from graphql_relay import from_global_id

from devind_helpers.schema.types import ConsumerActionType
from devind_helpers.decorators import permission_classes
from devind_helpers.orm_utils import get_object_or_404
from devind_helpers.permissions import IsAuthenticated
from devind_helpers.schema.mutations import BaseMutation
from devind_notifications.models import Notice
from devind_notifications.permissions import DeleteNotice
from devind_notifications.schema.subscriptions import NotificationsSubscription


class DeleteNoticeMutation(BaseMutation):
    """Удаление всех уведомлений"""

    class Input:
        notice_id = graphene.ID(required=True, description='Идентификатор уведомления')

    @staticmethod
    @permission_classes([IsAuthenticated, DeleteNotice])
    def mutate_and_get_payload(root, info: ResolveInfo, notice_id: str):
        notice_id = from_global_id(notice_id)[1]
        notice: Notice = get_object_or_404(Notice, pk=notice_id)
        info.context.check_object_permissions(info.context, notice)
        for notification in notice.notification_set.all():
            NotificationsSubscription.notify(
                f'notification.{notification.user_id}',
                ConsumerActionType.DELETE,
                notification.id
            )
        notice.delete()
        return DeleteNoticeMutation()
