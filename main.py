#!/usr/bin/env python3
import json

import discord
from discord.ext import commands

from music import MusicCog

bot = commands.Bot(command_prefix='!', description="A music bot")

@bot.event
async def on_ready():
    activity = discord.Game(name='!play something')
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user.name}')
    bot.add_cog(MusicCog(bot))

def main():
    with open('config.json') as fh:
        bot.config = json.load(fh)

    bot.run(bot.config['token'])


if __name__ == "__main__":
    main()