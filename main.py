import os

import discord
from discord.ext import commands

from database import engine
from models.config import config
from models.db_models import Base


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="\x00", intents=discord.Intents.all())

    async def setup_hook(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        guild = discord.Object(id=config.DISCORD_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


bot = Bot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.CustomActivity(name="🦋 Watching over your notes..."),
        status=discord.Status.idle,
    )


bot.run(config.DISCORD_TOKEN)
