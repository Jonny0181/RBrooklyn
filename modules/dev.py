import discord
from discord.ext import commands
from subprocess import check_output, CalledProcessError
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

    async def on_message(self, message):
        author = message.author
        try:
            color = author.color
        except:
            color = 0x585858
        if author.id == self.bot.user.id:
            embed=discord.Embed(description=message.content.replace("```", ""), color=color)
            await self.bot.edit_message(message, new_content=" ", embed=embed)

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def pip(self, ctx):
        """Pip tools."""
        if ctx.invoked_subcommand is None:
            await self.bot.say(embed=discord.Embed(description="""b!pip

Pip tools.

Commands:
  upgrade   Upgrade pip programs for Python 3.5
  uninstall Uninstall pip programs for Python 3.5
  install   Install pip programs for Python 3.5

Type b!help command for more info on a command.
You can also type b!help category for more info on a category."""))
            
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
