import discord
from discord.ext import commands
from discord import app_commands

# TODO: Add confirmation modal


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="init",
        description="Initializes the server. Destroys all existing notes and channels.",
    )
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
