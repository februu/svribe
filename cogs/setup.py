import discord
from discord import app_commands
from discord.ext import commands

from services.settings import (
    set_files_category_id,
    set_inbox_channel_id,
    set_links_category_id,
    set_notes_category_id,
)

# TODO: Add confirmation modal


class SettingsModal(discord.ui.Modal, title="Server Settings"):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild

        self.notes_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.category], required=True
        )
        self.links_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.category], required=True
        )
        self.files_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.category], required=True
        )
        self.inbox_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.text], required=True
        )

        self.add_item(discord.ui.Label(text="Notes category", component=self.notes_select))
        self.add_item(discord.ui.Label(text="Links category", component=self.links_select))
        self.add_item(discord.ui.Label(text="Files category", component=self.files_select))
        self.add_item(discord.ui.Label(text="Inbox channel", component=self.inbox_select))

    async def on_submit(self, interaction: discord.Interaction):
        notes_category = self.notes_select.values[0]
        links_category = self.links_select.values[0]
        files_category = self.files_select.values[0]
        inbox_channel = self.inbox_select.values[0]

        await set_notes_category_id(self.guild.id, notes_category.id)
        await set_links_category_id(self.guild.id, links_category.id)
        await set_files_category_id(self.guild.id, files_category.id)
        await set_inbox_channel_id(self.guild.id, inbox_channel.id)

        await interaction.response.send_message(
            f"### Settings updated!\n"
            f"**Notes:** {notes_category.name}\n"
            f"**Links:** {links_category.name}\n"
            f"**Files:** {files_category.name}\n"
            f"**Inbox channel:** {inbox_channel.mention}",
            ephemeral=True,
        )


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="init",
        description="Initializes the server. Destroys all existing notes and channels.",
    )
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def init(self, interaction: discord.Interaction):
        """Initializes the server by deleting all existing channels and creating the necessary categories and channels."""
        await interaction.response.send_message(
            "Server will be initialized in a moment!"
        )

        guild = interaction.guild
        if guild is None:
            await interaction.followup.send(
                "This command can only be used in a server."
            )
            return

        for channel in guild.channels:
            await channel.delete()

        for category in guild.categories:
            await category.delete()

        await guild.create_text_channel("inbox")

        notes_category = await guild.create_category("notes")
        await guild.create_text_channel("uncategorized", category=notes_category)

        links_category = await guild.create_category("links")
        await guild.create_text_channel("uncategorized", category=links_category)

        files_category = await guild.create_category("files")
        await guild.create_text_channel("images", category=files_category)
        await guild.create_text_channel("audio", category=files_category)
        await guild.create_text_channel("video", category=files_category)
        await guild.create_text_channel("docs", category=files_category)
        await guild.create_text_channel("uncategorized", category=files_category)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if not isinstance(error, app_commands.CheckFailure):
            raise error

    @app_commands.command(
            name="settings",
            description="Sets the notes/links/files categories and inbox channel for the server.",
        )
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def settings(self, interaction: discord.Interaction):
        """Sets the notes/links/files categories and inbox channel for the server."""

        assert interaction.guild is not None, "This command can only be used in a server."
        await interaction.response.send_modal(SettingsModal(interaction.guild))


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
