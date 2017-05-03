import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def rip(self, ctx, user: discord.User = None):
        """Rest in peace m8."""
        if user is not None:
            user = user.display_name
        else:
            user = ctx.message.author.display_name
        await ctx.send("<http://ripme.xyz/{}>".format(user.replace(" ", "%20")))
        
def setup(bot):
    bot.add_cog(Fun(bot))
