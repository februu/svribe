from dataclasses import dataclass

import discord


@dataclass
class MessageCategory:
    name: str
    description: str
    channel: discord.TextChannel
