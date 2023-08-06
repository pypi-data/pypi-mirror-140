from .base_dispatch import BaseDispatch


class TelegramDispatch(BaseDispatch):
    """Отправитель оповещения через телеграмм"""

    def send(self):
        print('Отправлено через телеграмм')
