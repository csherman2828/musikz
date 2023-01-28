#!/usr/bin/env python3
import json
from sys import argv

import discord
from discord.ext import commands

import music

_config = None
_token = ''
with open('config.json') as fh:
    _config = json.load(fh)

if __name__ == "__main__" and len(argv) > 1 and argv[1] == 'dev':
    _command_prefix = '?'
    _token = _config['dev_token']
else:
    _command_prefix = '!'
    _token = _config['token']

bot = commands.Bot(command_prefix=_command_prefix, description="Daj eno zgodlej")

@bot.event
async def on_ready():
    activity = discord.Game(name='|play sampanjac')
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user.name}')
    bot.add_cog(music.Music(bot))

def main():
    bot.run(_token)


if __name__ == "__main__":
    main()