from sqlalchemy import select

from database import async_session
from models.db_models import GuildSettings


async def _get_config(session, guild_id: int) -> GuildSettings | None:
    return await session.scalar(
        select(GuildSettings).where(GuildSettings.guild_id == guild_id)
    )


async def _get_or_create_config(session, guild_id: int) -> GuildSettings:
    config = await _get_config(session, guild_id)
    if config is None:
        config = GuildSettings(guild_id=guild_id)
        session.add(config)
    return config


async def get_inbox_channel_id(guild_id: int) -> int | None:
    """Get the inbox channel ID for a given guild."""
    async with async_session() as session:
        config = await _get_config(session, guild_id)
        return config.inbox_channel_id if config else None


async def set_inbox_channel_id(guild_id: int, channel_id: int | None) -> None:
    """Set the inbox channel ID for a given guild."""
    async with async_session() as session:
        config = await _get_or_create_config(session, guild_id)
        config.inbox_channel_id = channel_id
        await session.commit()


async def get_notes_category_id(guild_id: int) -> int | None:
    """Get the notes category ID for a given guild."""
    async with async_session() as session:
        config = await _get_config(session, guild_id)
        return config.notes_category_id if config else None


async def set_notes_category_id(guild_id: int, category_id: int | None) -> None:
    """Set the notes category ID for a given guild."""
    async with async_session() as session:
        config = await _get_or_create_config(session, guild_id)
        config.notes_category_id = category_id
        await session.commit()


async def get_links_category_id(guild_id: int) -> int | None:
    """Get the links category ID for a given guild."""
    async with async_session() as session:
        config = await _get_config(session, guild_id)
        return config.links_category_id if config else None


async def set_links_category_id(guild_id: int, category_id: int | None) -> None:
    """Set the links category ID for a given guild."""
    async with async_session() as session:
        config = await _get_or_create_config(session, guild_id)
        config.links_category_id = category_id
        await session.commit()


async def get_files_category_id(guild_id: int) -> int | None:
    """Get the files category ID for a given guild."""
    async with async_session() as session:
        config = await _get_config(session, guild_id)
        return config.files_category_id if config else None


async def set_files_category_id(guild_id: int, category_id: int | None) -> None:
    """Set the files category ID for a given guild."""
    async with async_session() as session:
        config = await _get_or_create_config(session, guild_id)
        config.files_category_id = category_id
        await session.commit()
