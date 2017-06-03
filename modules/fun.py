import discord
import asyncio
import random as rng
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lenny(self):
        """Displays a random lenny face."""
        lenny = rng.choice([
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
            "ヽ༼ຈل͜ຈ༽ﾉ"
        ])
        await self.bot.say(lenny)

    @commands.command()
    async def choose(self, *choices):
        """Chooses between multiple choices.
        To denote multiple choices, you should use double quotes.
        """
        if len(choices) < 2:
            await self.bot.say('Not enough choices to pick from.')
        else:
            await self.bot.say(rng.choice(choices))
        
    @commands.command(pass_context=True)
    async def rip(self, ctx, user: discord.User = None):
        """Rest in peace m8."""
        if user is not None:
            user = user.display_name
        else:
            user = ctx.message.author.display_name
        await self.bot.say("<http://ripme.xyz/{}>".format(user.replace(" ", "%20")))

    @commands.command(pass_context=True)
    async def bomb(self, ctx, user : discord.User = None):
        """Allahu Akbar!"""
        if user is not None:
            user = user.mention
            msg = ":boom: {} has suicide bombed {}".format(ctx.message.author.display_name, user)
        else:
            user = ctx.message.author.mention
            msg = ":boom: {} has commited suicide on a public bus!".format(user)
        ok = await self.bot.say(":bomb:")
        await asyncio.sleep(2)
        await self.bot.edit_message(ok, msg)

    @commands.command(pass_context=True, no_pm=True)
    async def cookie(self, ctx, *, user: discord.Member):
        await self.bot.say("**You have given {} a cookie! | :cookie:**".format(user.mention))

        
def setup(bot):
    bot.add_cog(Fun(bot))
