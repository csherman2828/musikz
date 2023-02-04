#!/usr/bin/env python3

import discord
from discord.ext import commands

from music import MusicCog
from config import token, prefix

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=prefix, 
    description="A music bot", 
    intents=intents
)

@bot.event
async def on_ready():
    activity = discord.Game(name='!play something')
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user.name}')
    # bot.add_cog(MusicCog(bot))

def main():
    bot.run(token)

if __name__ == "__main__":
    main()