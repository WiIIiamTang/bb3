import discord
import youtube_related
import random
import logging
import asyncio
from discord.ext import commands

from src.cogs.Music.ytdl import YTDLSource
from src.util.constants import BB3_MAX_RADIO_PLAY_COUNT

logger = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_url_radio = None  # TODO: Temporary

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play_local(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(
            source, after=lambda e: print(f"Player error: {e}") if e else None
        )

        await ctx.send(f"Now playing: {query}")

    @commands.command(aliases=["dp"])
    async def dplay(self, ctx, *, url):
        """Downloads and plays from a url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        """Streams from a url (doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    async def play_next(self, ctx, url, count):
        if count <= 0:
            return

        related = await youtube_related.async_fetch(url)
        related_id = random.choice(related).get("id")
        url = f"https://www.youtube.com/watch?v={related_id}"

        logger.info(f"Playing next song for {ctx.author.name}")
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.current_url_radio = url
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(ctx, url, count - 1), self.bot.loop
            ),
        )
        await ctx.send(f"Now playing: {player.title} {url}")

    @commands.command(aliases=["nr"])
    async def next_radio(self, ctx):
        await self.stop(ctx)
        if self.current_url_radio is None:
            await ctx.send("No radio is playing")
            return
        await self.radio(ctx, url=self.current_url_radio)

    @commands.command(aliases=["r"])
    async def radio(self, ctx, *, url, count=BB3_MAX_RADIO_PLAY_COUNT):
        """Streams from a url and plays a related song after"""

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.current_url_radio = url
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(ctx, url, count - 1), self.bot.loop
            ),
        )
        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def send_related(self, ctx, *, url):
        """Sends a related song from a url"""

        related = await youtube_related.async_fetch(url)
        related_id = related[0].get("id")
        await ctx.send(f"https://www.youtube.com/watch?v={related_id}")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @dplay.before_invoke
    @play_local.before_invoke
    @radio.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
