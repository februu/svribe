import discord
from discord import app_commands
from discord.ext import commands

from models.destination import Destination
from services.files import get_file_destination
from services.links import get_link_destination, has_link
from services.notes import get_note_destination


async def get_destinations_from_category(
    guild: discord.Guild, category_name: str
) -> list[Destination]:
    """Returns a list of Destination objects for the given Discord category."""
    discord_category = discord.utils.get(guild.categories, name=category_name)
    if discord_category is None:
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

    if message.channel.name != "inbox":
        return

    if message.attachments:
        available_destinations = await get_destinations_from_category(
            message.guild, "files"
        )
        destination = await get_file_destination(
            message.attachments, available_destinations
        )
    elif has_link(message.content):
        available_destinations = await get_destinations_from_category(
            message.guild, "links"
        )
        destination = await get_link_destination(
            message.content, available_destinations
        )
    else:
        available_destinations = await get_destinations_from_category(
            message.guild, "notes"
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
