import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Configuration for the application."""

    GEMINI_API_KEY: str
    DISCORD_TOKEN: str
    DISCORD_GUILD_ID: int
    DATABASE_PATH: str


def require_env_var(var_name: str) -> str:
    """Get an environment variable or raise an error if it's not set."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' is required but not set.")
    return value


load_dotenv()
config = Config(
    GEMINI_API_KEY=require_env_var("GEMINI_API_KEY"),
    DISCORD_TOKEN=require_env_var("DISCORD_TOKEN"),
    DISCORD_GUILD_ID=int(require_env_var("DISCORD_GUILD_ID")),
    DATABASE_PATH=os.getenv("DATABASE_PATH", "./data/svribe.db")
)
