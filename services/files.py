import discord
from typing import Iterable

from models.message_category import MessageCategory
from services.llm import get_category


async def get_file_category(
    attachments: list[discord.Attachment], categories: Iterable[MessageCategory]
) -> MessageCategory | None:
    """Gets the category for a given list of attachments."""
    filenames = "\n".join(f"- {a.filename.split('.')[-1].lower()}" for a in attachments)
    return await get_category(filenames, categories)
