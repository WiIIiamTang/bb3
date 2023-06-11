import discord
from discord.ext import commands
import os
import logging
import logging.handlers

from src.cogs.Music.music import Music
from src.util.constants import (
    BB3_LOG_NAME,
    BB3_MAX_LOG_SIZE,
    BB3_MAX_LOG_COUNT,
    BB3_BOT_DESCRIPTION,
)

logger = logging.getLogger("bb3_bot")


def setup_logging():
    handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(os.getcwd(), "logs", BB3_LOG_NAME),
        encoding="utf-8",
        mode="a",
        maxBytes=BB3_MAX_LOG_SIZE,
        backupCount=BB3_MAX_LOG_COUNT,
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s][%(name)s]: %(message)s",
        handlers=[handler],
    )

    gateway_logger = logging.getLogger("discord.gateway")
    gateway_logger.setLevel(logging.INFO)


def create_bot(prefix):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(prefix),
        description=BB3_BOT_DESCRIPTION,
        intents=intents,
        log_handler=None,
    )

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    return bot


async def main(token, prefix="!"):
    setup_logging()
    bot = create_bot(prefix=prefix)
    logger.info(f"Created bot with prefix {prefix}")
    async with bot:
        await bot.add_cog(Music(bot))
        logger.info("Added Music cog")

        await bot.start(token=token)
