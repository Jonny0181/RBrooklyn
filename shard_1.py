import os
import re
import json
import time
import asyncio
import discord
import datetime
from utils import checks
from discord.ext import commands
from random import choice as randchoice

prefix = "b!"
description = ''
shard_id = 0
shard_count = 2
bot = commands.Bot(command_prefix=(prefix), description=description, shard_id=shard_id, shard_count=shard_count)
starttime = time.time()
starttime2 = time.ctime(int(time.time()))
bot.pm_help = True
wrap = "```py\n{}\n```"


modules = [
    'modules.music',
    'modules.info',
    'modules.modlog',
    'modules.mod']

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

class Default():
    def __init__(self, bot):
        self.bot = bot

@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Alright, loading {}".format(module))
            bot.load_extension(module)
            await bot.say("Loading finished!")
        else:
            await bot.say("You can't load a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """Unloads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, unloading {}".format(module))
            bot.unload_extension(module)
            await bot.say("Unloading finished!")
        else:
            await bot.say("You can't unload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))
        
@bot.command(hidden=True)
@checks.is_owner()
async def reload(*, module: str):
    """Reloads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, reloading {}".format(module))
            bot.unload_extension(module)
            bot.load_extension(module)
            await bot.say("Reloading finished!")
        else:
            await bot.say("You can't reload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def debug(ctx, *, code: str):
    """Evaluates code."""
    try:
        result = eval(code)
        if code.lower().startswith("print"):
            result
        elif asyncio.iscoroutine(result):
            await result
        else:
            await bot.say(wrap.format(result))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setname(ctx, *, name: str):
    """Sets the bots name."""
    try:
        await bot.edit_profile(username=name)
        await bot.say("Username successfully changed to `{}`".format(name))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

bot.add_cog(Default(bot))
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.login(""))
    loop.run_until_complete(bot.connect())
except Exception:
    loop.run_until_complete(os.system("main.py"))
finally:
    loop.close()
