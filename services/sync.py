import discord
from sqlalchemy import select

from database import async_session
from models.db_models import Channel, DiscordCategory


async def upsert_category(category: discord.CategoryChannel) -> None:
    """Inserts or updates the DB mirror row for a Discord category."""
    async with async_session() as session:
        existing = await session.get(DiscordCategory, category.id)
        if existing is None:
            session.add(
                DiscordCategory(
                    discord_category_id=category.id,
                    name=category.name,
                    position=category.position,
                )
            )
        else:
            existing.name = category.name
            existing.position = category.position
        await session.commit()


async def delete_category(category_id: int) -> None:
    """Removes the DB mirror row for a deleted Discord category."""
    async with async_session() as session:
        existing = await session.get(DiscordCategory, category_id)
        if existing is not None:
            await session.delete(existing)
            await session.commit()


async def upsert_channel(channel: discord.TextChannel) -> None:
    """Inserts or updates the DB mirror row for a Discord text channel."""
    async with async_session() as session:
        existing = await session.get(Channel, channel.id)
        if existing is None:
            session.add(
                Channel(
                    discord_channel_id=channel.id,
                    parent_category_id=channel.category_id,
                    name=channel.name,
                    topic=channel.topic or "",
                    position=channel.position,
                )
            )
        else:
            existing.parent_category_id = channel.category_id
            existing.name = channel.name
            existing.topic = channel.topic or ""
            existing.position = channel.position
        await session.commit()


async def delete_channel(channel_id: int) -> None:
    """Removes the DB mirror row for a deleted Discord text channel."""
    async with async_session() as session:
        existing = await session.get(Channel, channel_id)
        if existing is not None:
            await session.delete(existing)
            await session.commit()


async def resync_guild(guild: discord.Guild) -> None:
    """Reconciles the DB mirror with the guild's current live state."""
    for category in guild.categories:
        await upsert_category(category)
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            await upsert_channel(channel)

    live_category_ids = {category.id for category in guild.categories}
    live_channel_ids = {
        channel.id
        for channel in guild.channels
        if isinstance(channel, discord.TextChannel)
    }

    async with async_session() as session:
        mirrored_category_ids = await session.scalars(
            select(DiscordCategory.discord_category_id)
        )
        stale_category_ids = [
            cid for cid in mirrored_category_ids if cid not in live_category_ids
        ]

        mirrored_channel_ids = await session.scalars(
            select(Channel.discord_channel_id)
        )
        stale_channel_ids = [
            cid for cid in mirrored_channel_ids if cid not in live_channel_ids
        ]

    for category_id in stale_category_ids:
        await delete_category(category_id)
    for channel_id in stale_channel_ids:
        await delete_channel(channel_id)
