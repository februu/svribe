from collections.abc import Iterable

import discord

from models.destination import Destination
from services.llm import get_destination


async def get_file_destination(
    attachments: list[discord.Attachment], destinations: Iterable[Destination]
) -> Destination | None:
    """Gets the destination for a given list of attachments."""
    filenames = "\n".join(f"- {a.filename.split('.')[-1].lower()}" for a in attachments)
    return await get_destination(filenames, destinations)
