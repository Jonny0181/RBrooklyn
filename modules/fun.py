import discord
import asyncio
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
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
        
def setup(bot):
    bot.add_cog(Fun(bot))
