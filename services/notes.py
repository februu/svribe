from typing import Iterable

from services.llm import get_category_from_text


async def get_note_category(message: str, categories: Iterable[str]) -> str | None:
    """Gets the category for a given note message."""
    return await get_category_from_text(message, categories)
