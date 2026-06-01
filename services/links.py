import re
from typing import Iterable

from services.llm import get_category_from_text

URL_PATTERN = re.compile(
    r"https?://"  # must have protocol
    r'[^\s<>"\'`]+'  # match until whitespace or discord markdown chars
    r"(?<![.,;!?)\]])",  # strip trailing punctuation
    re.IGNORECASE,
)


def has_link(text: str) -> bool:
    """Checks if a Discord message contains a URL."""
    return bool(URL_PATTERN.search(text))


async def get_link_category(message: str, categories: Iterable[str]) -> str | None:
    """Gets the category for a given message containing a link."""
    # TODO: Fetch the link preview and use the title/description/Open Graph tags for better categorization
    return await get_category_from_text(message, categories)
