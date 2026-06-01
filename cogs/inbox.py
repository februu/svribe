import discord
from discord.ext import commands
from discord import app_commands

from services.files import get_file_category
from services.links import get_link_category, has_link
from services.notes import get_note_category


async def get_text_channels_in_category(
    guild: discord.Guild, category_name: str
) -> dict[str, discord.TextChannel]:
    """Returns a mapping of lowercase channel names to TextChannel objects for the given discord category name."""
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        return {}
    return {
        channel.name.lower(): channel
        for channel in category.channels
        if isinstance(channel, discord.TextChannel)
    }


async def handle_incoming_message(message: discord.Message):
    """Handles incoming messages in the inbox channel, categorizes them, and moves them to the appropriate channel."""
    if message.author.bot or message.guild is None:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.name != "inbox":
        return

    if message.attachments:
        target_categories = await get_text_channels_in_category(message.guild, "files")
        message_category = await get_file_category(
            message.attachments, target_categories.keys()
        )
    elif has_link(message.content):
        target_categories = await get_text_channels_in_category(message.guild, "links")
        message_category = await get_link_category(
            message.content, target_categories.keys()
        )
    else:
        target_categories = await get_text_channels_in_category(message.guild, "notes")
        message_category = await get_note_category(
            message.content, target_categories.keys()
        )

    if not message_category:
        await message.channel.send("Cannot determine category for the message.")
        return

    target_channel = target_categories.get(message_category)
    assert target_channel is not None, (
        "Target channel should exist based on category detection"
    )
    await target_channel.send(
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
