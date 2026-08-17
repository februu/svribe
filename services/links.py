import re
from collections.abc import Iterable

import tldextract

from models.destination import Destination
from services.llm import get_destination

URL_PATTERN = re.compile(
    r"https?://"  # must have protocol
    r'[^\s<>"\'`]+'  # match until whitespace or discord markdown chars
    r"(?<![.,;!?)\]])",  # strip trailing punctuation
    re.IGNORECASE,
)


def has_link(text: str) -> bool:
    """Checks if a Discord message contains a URL."""
    return bool(URL_PATTERN.search(text))


def _extract_domain_from_message(url: str) -> str | None:
    """Extracts the domain name (e.g. "instagram") from a URL."""
    extracted = tldextract.extract(url)
    return extracted.domain or None


def _count_urls(text: str) -> int:
    """Counts URLs in a string."""
    return len(URL_PATTERN.findall(text))


async def get_link_destination(
    message: str, destinations: Iterable[Destination]
) -> Destination | None:
    """Gets the destination for a given message containing a link."""
    # TODO: Fetch the link preview and use the title/description/Open Graph tags for better categorization

    if not has_link(message):
        return None

    if _count_urls(message) > 1:
        return await get_destination(message, destinations)

    domain = _extract_domain_from_message(message)
    if domain:
        for destination in destinations:
            if domain in destination.name:
                return destination

    return await get_destination(message, destinations)
