import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


class Cleaner:
    bot: Bot
    chat_id: str

    def __init__(self, limit: int = 10):
        if limit <= 0:
            raise ValueError('The limit cannot be less or equal to `0`')

        self.limit = limit
        self._messages: dict[str, list[int]] = {}

    def __str__(self) -> str:
        """Get string representation of the object."""
        return f"<{__class__.__name__} limit:{self.limit}>"

    def __repr__(self) -> str:
        """Get string representation of the object."""
        return self.__str__()

    @property
    def chat_id(self) -> str:
        """Get the chat id."""
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value: str | int):
        """Set the chat id."""
        self._chat_id = str(value)
        if value is not None:
            self._messages[self._chat_id]: list[int] = self._messages.get(self._chat_id, [])

    @property
    def messages_for_chat(self) -> list:
        """Get list of messages for the chat."""
        if self._chat_id not in self._messages:
            raise ValueError("Can't get list of messages, chat not found")

        return self._messages.get(self._chat_id, [])

    async def add(self, message_id: int):
        """Add a message to the chat."""
        if len(self.messages_for_chat) >= self.limit:
            await self._del()

        self.messages_for_chat.append(message_id)

    async def _del(self, message_id: Optional[int] = None):
        """Delete a message from the chat."""
        if self.bot is None:
            raise ValueError("Cannot delete message, `bot` does not exist.")

        try:
            if message_id is not None:
                if message_id in self.messages_for_chat:
                    await self.bot.delete_message(chat_id=self.chat_id, message_id=message_id)
                else:
                    raise ValueError(f"Message with message_id {message_id} not found in self.messages_for_chat")
            else:
                if self.messages_for_chat:
                    """If self.messages_for_chat is not empty, delete the first message in self"""
                    message_id = self.messages_for_chat.pop(0)
                    await self.bot.delete_message(chat_id=self.chat_id, message_id=message_id)
                else:
                    raise ValueError("No message_id provided, and self.messages_for_chat is empty.")
        except TelegramBadRequest as exc:
            if (
                    "message to delete not found" in exc.message or
                    "message can't be deleted" in exc.message
            ):
                logger.error('Cannot delete messages')
            else:
                raise

    async def message_clear(self):
        self.messages_for_chat.clear()

    async def purge(self):
        """Delete all messages from the chat."""
        for message_id in self.messages_for_chat:
            await self._del(message_id=message_id)

        self.messages_for_chat.clear()