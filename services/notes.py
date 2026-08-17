from collections.abc import Iterable

from models.destination import Destination
from services.llm import get_destination


async def get_note_destination(
    message: str, destinations: Iterable[Destination]
) -> Destination | None:
    """Gets the destination for a given note message."""
    return await get_destination(message, destinations)
