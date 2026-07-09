from typing import Iterable

from models.message_category import MessageCategory
from services.llm import get_category


async def get_note_category(
    message: str, categories: Iterable[MessageCategory]
) -> MessageCategory | None:
    """Gets the category for a given note message."""
    return await get_category(message, categories)
