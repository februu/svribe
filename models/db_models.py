from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GuildSettings(Base):
    """Assigns Discord categories/channels to their functional role in the app."""

    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(primary_key=True)
    notes_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("discord_categories.discord_category_id", ondelete="SET NULL")
    )
    links_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("discord_categories.discord_category_id", ondelete="SET NULL")
    )
    files_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("discord_categories.discord_category_id", ondelete="SET NULL")
    )
    inbox_channel_id: Mapped[int | None] = mapped_column(
        ForeignKey("channels.discord_channel_id", ondelete="SET NULL")
    )


class DiscordCategory(Base):
    """Mirrors a Discord category."""

    __tablename__ = "discord_categories"

    discord_category_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    position: Mapped[int]


class Channel(Base):
    """Mirrors a Discord text channel."""

    __tablename__ = "channels"

    discord_channel_id: Mapped[int] = mapped_column(primary_key=True)
    parent_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("discord_categories.discord_category_id", ondelete="SET NULL")
    )
    name: Mapped[str]
    topic: Mapped[str]
    position: Mapped[int]


class Message(Base):
    """Mirrors a Discord message, kept for drift detection and full server restore."""

    __tablename__ = "messages"

    discord_message_id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.discord_channel_id", ondelete="CASCADE")
    )
    content: Mapped[str]
    created_at: Mapped[datetime]
    edited_at: Mapped[datetime | None]
    attachments: Mapped[list[Attachment]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class Attachment(Base):
    """An attachment belonging to a synced message, cached locally for restore."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.discord_message_id", ondelete="CASCADE")
    )
    filename: Mapped[str]
    local_path: Mapped[str]
    message: Mapped[Message] = relationship(back_populates="attachments")


class CategorizationCacheEntry(Base):
    """Caches an LLM categorization decision for a file extension or link domain.

    Keyed on the stable Discord channel id (not the channel name), so renaming a
    channel does not invalidate its cache entries -- only deleting it does, via the
    ON DELETE CASCADE below.
    """

    __tablename__ = "categorization_cache"
    __table_args__ = (CheckConstraint("key_type IN ('extension', 'domain')"),)

    key_type: Mapped[str] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.discord_channel_id", ondelete="CASCADE")
    )
    cached_at: Mapped[datetime] = mapped_column(server_default=func.now())
