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
        
    def _list_cogs(self):
        cogs = [os.path.basename(f) for f in glob.glob("modules/*.py")]
        return ["modules." + os.path.splitext(f)[0] for f in cogs]

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def modules(self, ctx):
        """Shows Brooklyns modules."""
        loaded = [c.__module__.split(".") for c in self.bot.cogs.values()]
        unloaded = [c.split(".") for c in self._list_cogs()
                    if c.split(".") not in loaded]
        if not unloaded:
            unloaded = ["None"]
        msg=discord.Embed(description="**Showing modules for Brooklyn.**", colour=discord.Colour(value=colour))
        msg.add_field(name="Loaded", value="{}".format(", ".join(sorted(loaded))))
        msg.add_field(name="Unloaded", value="{}".format(", ".join(sorted(unloaded))))
        await self.bot.say(embed=msg)

def setup(bot):
    bot.add_cog(Dev(bot))
