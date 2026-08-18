import discord
from discord import app_commands
from discord.ext import commands

from models.destination import Destination
from services.files import get_file_destination
from services.links import get_link_destination, has_link
from services.notes import get_note_destination
from services.settings import (
    get_files_category_id,
    get_inbox_channel_id,
    get_links_category_id,
    get_notes_category_id,
)


async def get_destinations_from_category(
    guild: discord.Guild, category_id: int | None
) -> list[Destination]:
    """Returns a list of Destination objects for the given Discord category."""
    if category_id is None:
        return []
    discord_category = guild.get_channel(category_id)
    if not isinstance(discord_category, discord.CategoryChannel):
        return []
    return [
        Destination(
            name=channel.name.lower(),
            description=channel.topic or "",
            channel=channel,
        )
        for channel in discord_category.channels
        if isinstance(channel, discord.TextChannel)
    ]


async def handle_incoming_message(message: discord.Message):
    """Handles incoming messages in the inbox channel, categorizes them, and moves them to the appropriate channel."""
    if message.author.bot or message.guild is None:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    inbox_channel_id = await get_inbox_channel_id(message.guild.id)
    if message.channel.id != inbox_channel_id:
        return

    if message.attachments:
        files_category_id = await get_files_category_id(message.guild.id)
        available_destinations = await get_destinations_from_category(
            message.guild, files_category_id
        )
        destination = await get_file_destination(
            message.attachments, available_destinations
        )
    elif has_link(message.content):
        links_category_id = await get_links_category_id(message.guild.id)
        available_destinations = await get_destinations_from_category(
            message.guild, links_category_id
        )
        destination = await get_link_destination(
            message.content, available_destinations
        )
    else:
        notes_category_id = await get_notes_category_id(message.guild.id)
        available_destinations = await get_destinations_from_category(
            message.guild, notes_category_id
        )
        destination = await get_note_destination(
            message.content, available_destinations
        )

    if not destination:
        await message.channel.send("Cannot determine a destination for the message.")
        return

    await destination.channel.send(
        message.content,
        files=[await attachment.to_file() for attachment in message.attachments],
    )
    await message.delete()


class Inbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if not isinstance(error, app_commands.CheckFailure):
            raise error

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await handle_incoming_message(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Inbox(bot))
