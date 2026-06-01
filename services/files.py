import discord
from typing import Iterable

from services.llm import get_category_from_text


async def get_file_category(
    attachments: list[discord.Attachment], categories: Iterable[str]
) -> str | None:
    """Gets the category for a given list of attachments."""
    filenames = "\n".join(f"- {a.filename.split('.')[-1].lower()}" for a in attachments)
    return await get_category_from_text(filenames, categories)
