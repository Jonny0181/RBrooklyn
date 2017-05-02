import discord
from discord.ext import commands
from utils import checks

class Dev:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hide=True)
    @checks.is_owner()
    async def setavatar(self, *, url: str):
    """Change the bot's avatar."""
        avatar = await get_file(url)
        await self.bot.edit_profile(avatar=avatar)
        await self.bot.say("Changed avatar.")
        
def setup(bot):
    bot.add_cog(Dev(bot))
