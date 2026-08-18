import discord
from discord import app_commands
from discord.ext import commands

from models.config import config
from services.sync import (
    delete_category,
    delete_channel,
    resync_guild,
    upsert_category,
    upsert_channel,
)


class Synchronization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if not isinstance(error, app_commands.CheckFailure):
            raise error

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(config.DISCORD_GUILD_ID)
        if guild is not None:
            await resync_guild(guild)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if isinstance(channel, discord.CategoryChannel):
            await upsert_category(channel)
        elif isinstance(channel, discord.TextChannel):
            await upsert_channel(channel)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if isinstance(channel, discord.CategoryChannel):
            await delete_category(channel.id)
        elif isinstance(channel, discord.TextChannel):
            await delete_channel(channel.id)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ):
        if isinstance(after, discord.CategoryChannel):
            await upsert_category(after)
        elif isinstance(after, discord.TextChannel):
            await upsert_channel(after)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message): ...

    @commands.Cog.listener()
    async def on_raw_message_delete(self, message: discord.RawMessageDeleteEvent): ...

    # TODO: Sync messages (on_message/on_raw_message_delete/on_raw_message_edit)
    # into the messages/attachments tables, downloading attachments to local
    # storage per the restore design.


async def setup(bot: commands.Bot):
    await bot.add_cog(Synchronization(bot))
