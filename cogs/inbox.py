import discord
from discord import app_commands
from discord.ext import commands

from models.message_category import MessageCategory
from services.files import get_file_category
from services.links import get_link_category, has_link
from services.notes import get_note_category


async def get_message_categories_from_category_channel(
    guild: discord.Guild, category_name: str
) -> list[MessageCategory]:
    """Returns a list of MessageCategory objects for the given discord category."""
    discord_category = discord.utils.get(guild.categories, name=category_name)
    if discord_category is None:
        return []
    return [
        MessageCategory(
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
        available_categories = await get_message_categories_from_category_channel(
            message.guild, "files"
        )
        message_category = await get_file_category(
            message.attachments, available_categories
        )
    elif has_link(message.content):
        available_categories = await get_message_categories_from_category_channel(
            message.guild, "links"
        )
        message_category = await get_link_category(
            message.content, available_categories
        )
    else:
        available_categories = await get_message_categories_from_category_channel(
            message.guild, "notes"
        )
        message_category = await get_note_category(
            message.content, available_categories
        )

    if not message_category:
        await message.channel.send("Cannot determine category for the message.")
        return

    await message_category.channel.send(
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
