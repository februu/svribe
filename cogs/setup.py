from typing import ClassVar

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


class SetCategoryModal(discord.ui.Modal, title="Set Category"):
    _ROLE_OPTIONS: ClassVar = [
        discord.SelectOption(label="Notes", value="notes"),
        discord.SelectOption(label="Links", value="links"),
        discord.SelectOption(label="Files", value="files"),
    ]

    _SETTERS: ClassVar = {
        "notes": set_notes_category_id,
        "links": set_links_category_id,
        "files": set_files_category_id,
    }

    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild

        self.role_select = discord.ui.Select(options=self._ROLE_OPTIONS)
        self.category_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.category], required=True
        )

        self.add_item(discord.ui.Label(text="Role", component=self.role_select))
        self.add_item(
            discord.ui.Label(text="Category", component=self.category_select)
        )

    async def on_submit(self, interaction: discord.Interaction):
        role = self.role_select.values[0]
        category = self.category_select.values[0]

        await self._SETTERS[role](self.guild.id, category.id)
        await interaction.response.send_message(
            f"{role.capitalize()} category set to {category.mention}!",
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
            name="set_inbox",
            description="Sets the inbox channel for the server.",
        )
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def set_inbox(self, interaction: discord.Interaction):
        """Sets the inbox channel for the server."""

        assert interaction.guild is not None, "This command can only be used in a server."
        assert interaction.channel is not None, "This command can only be used in a channel."
        await set_inbox_channel_id(interaction.guild.id, interaction.channel.id)
        await interaction.response.send_message(
            "Inbox channel set successfully!"
        )

    @app_commands.command(
            name="set_category",
            description="Sets the category for the server.",
        )
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def set_category(self, interaction: discord.Interaction):
        """Sets the notes/links/files categories for the server."""

        assert interaction.guild is not None, "This command can only be used in a server."

        await interaction.response.send_modal(SetCategoryModal(interaction.guild))


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
