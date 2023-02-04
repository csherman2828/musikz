# import math

from discord import app_commands
from discord.ext import commands

# import ytdl
# import voice


class MusicCog(commands.Cog, name="Music"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command(name='ping', description="Tests the bot's connection")
    async def _do_something(self, ctx):
        await ctx.send('pong')