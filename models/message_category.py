from dataclasses import dataclass

import discord


@dataclass(frozen=True)
class MessageCategory:
    """Represents a category that incoming messages can be classified into."""

    name: str
    description: str
    channel: discord.TextChannel
