from os.path import join
from typing import Optional, Type

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from devind_helpers.orm_utils import get_object_or_none

from devind_notifications.models import get_mailing_model, AbstractMailing

Mailing: Type[AbstractMailing] = get_mailing_model()


@shared_task(bind=True, default_retry_delay=300)
def send_mail(self, mailing_id: int) -> int:
    """Отправка email.

    :param self: задача
    :param mailing_id: идентификатор оповещения
    :return: количество отправленных писем
    """

    try:
        mailing: Optional[AbstractMailing] = get_object_or_none(Mailing, pk=mailing_id)
        if not mailing:
            return 0  # Писем не отправлено
        message: EmailMultiAlternatives = EmailMultiAlternatives(
            mailing.header,
            strip_tags(mailing.text),
            settings.EMAIL_HOST_USER,
            (mailing.address,)
        )
        message.attach_alternative(mailing.text, 'text/html')
        if mailing.attachments:
            for attach in mailing.attachments:
                message.attach_file(join(settings.BASE_DIR, attach.path))
        return message.send()
    except Exception as ex:
        raise self.retry(exc=ex)
