from dataclasses import dataclass

import discord


@dataclass(frozen=True)
class Destination:
    """Represents a channel that incoming messages can be routed to."""

    name: str
    description: str
    channel: discord.TextChannel

    def __post_init__(self):
        if not self.name == self.name.strip().lower():
            raise ValueError(
                "Destination name must be lowercase and cannot have leading or trailing whitespace."
            )
        if not self.name == self.channel.name.strip().lower():
            raise ValueError(
                "Destination name must match the associated channel name."
            )
        if self.name.lower() == "<none>":
            raise ValueError(
                "The name '<none>' is reserved and cannot be used for a destination."
            )
        if not self.description == self.description.strip():
            raise ValueError(
                "Destination description cannot have leading or trailing whitespace."
            )
