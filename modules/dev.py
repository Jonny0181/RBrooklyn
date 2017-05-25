import discord
import asyncio
from discord.ext import commands
from subprocess import check_output, CalledProcessError
from utils import checks
from utils.chat_formatting import pagify, box

wrap = "```py\n{}```"

class Dev:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code: str):
        """Evaluates code."""
        try:
            result = eval(code)
            if code.lower().startswith("print"):
                result
            elif asyncio.iscoroutine(result):
                await result
            else:
                e = discord.Embed(colour=discord.Colour.green())
                e.add_field(name="Input:", value=wrap.format(code), inline=False)
                e.add_field(name="Output:", value=wrap.format(result), inline=False)
                await self.bot.say(embed=e)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(description=wrap.format(type(e).__name__ + ': ' + str(e)), colour=discord.Colour.red()))

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
