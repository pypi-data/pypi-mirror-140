from abc import ABC, abstractmethod

from devind_notifications.models import Mailing


class BaseDispatch(ABC):
    """Базовый отправитель оповещений"""

    def __init__(self, mailing: Mailing):
        self.mailing = mailing

    @abstractmethod
    def send(self):
        """Отправка оповещения"""

        ...
