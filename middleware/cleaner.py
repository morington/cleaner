from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from cleaner import Cleaner


class CleanerMiddleware(BaseMiddleware):
    def __init__(self, cleaner: Cleaner):
        super().__init__()
        self.cleaner = cleaner

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        self.cleaner.bot = data.get('bot')
        self.cleaner.chat_id = data.get('event_chat').id

        data['cleaner']: Cleaner = self.cleaner

        return await handler(event, data)


