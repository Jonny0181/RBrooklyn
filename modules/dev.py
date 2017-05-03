import discord
from discord.ext import commands
from utils import checks

class Dev:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @checks.is_owner()
    async def setavatar(self, *, url: str):
        """Change the bot's avatar."""
        avatar = await get_file(url)
        await self.bot.edit_profile(avatar=avatar)
        await self.bot.say("Changed avatar.")

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def pip(self, ctx):
        """Pip tools."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            
    @pip.command()
    async def install(self, *, packagename):
        """Install pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {}".format(packagename), shell=True)
            await self.bot.say("`{}` installed succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

    @pip.command()
    async def uninstall(self, *, packagename):
        """Uninstall pip programs for Python 3.5"""
        try:
            output = check_output("pip3 uninstall {}".format(packagename), shell=True)
            await self.bot.say("`{}` uninstalled succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

    @pip.command()
    async def upgrade(self, *, packagename):
        """Upgrade pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {} --upgrade".format(packagename), shell=True)
            await self.bot.say("`{}` upgraded succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

def setup(bot):
    bot.add_cog(Dev(bot))
