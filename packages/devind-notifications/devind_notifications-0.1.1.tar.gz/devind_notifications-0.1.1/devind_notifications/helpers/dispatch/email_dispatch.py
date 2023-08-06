from typing import Optional, Type

from devind_core.models import get_setting_model, get_setting_value_model, AbstractSetting, AbstractSettingValue
from devind_helpers.orm_utils import get_object_or_none
from devind_helpers.utils import convert_str_to_bool
from .base_dispatch import BaseDispatch

Setting: Type[AbstractSetting] = get_setting_model()
SettingValue: Type[AbstractSettingValue] = get_setting_value_model()


class EmailDispatch(BaseDispatch):
    """Отправитель оповещения по email"""

    def send(self):
        from devind_notifications.tasks import send_mail
        setting: Optional[Setting] = get_object_or_none(Setting, key='NOTIFICATION_EMAIL')
        setting_value: Optional[SettingValue] = get_object_or_none(
            SettingValue,
            setting=setting,
            user=self.mailing.user
        )
        sv = convert_str_to_bool(setting.value if setting.readonly or setting_value is None else setting_value.value)
        if sv:
            send_mail.delay(self.mailing.pk)
