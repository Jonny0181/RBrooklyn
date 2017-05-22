import discord
from discord.ext import commands
from subprocess import check_output, CalledProcessError
from utils import checks
from utils.chat_formatting import pagify, box

class Dev:
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code):
        """Evaluates code"""
        def check(m):
            if m.content.strip().lower() == "more":
                return True

        author = ctx.message.author
        channel = ctx.message.channel

        code = code.strip('` ')
        result = None

        global_vars = globals().copy()
        global_vars['bot'] = self.bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        global_vars['server'] = ctx.message.server

        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await self.bot.say(box('{}: {}'.format(type(e).__name__, str(e)),
                                   lang="py"))
            return

        if asyncio.iscoroutine(result):
            result = await result

        result = str(result)

        if not ctx.message.channel.is_private:
            censor = (self.bot.settings.email,
                      self.bot.settings.password,
                      self.bot.settings.token)
            r = "[EXPUNGED]"
            for w in censor:
                if w is None or w == "":
                    continue
                result = result.replace(w, r)
                result = result.replace(w.lower(), r)
                result = result.replace(w.upper(), r)

        result = list(pagify(result, shorten_by=16))

        for i, page in enumerate(result):
            if i != 0 and i % 4 == 0:
                last = await self.bot.say("There are still {} messages. "
                                          "Type `more` to continue."
                                          "".format(len(result) - (i+1)))
                msg = await self.bot.wait_for_message(author=author,
                                                      channel=channel,
                                                      check=check,
                                                      timeout=10)
                if msg is None:
                    try:
                        await self.bot.delete_message(last)
                    except:
                        pass
                    finally:
                        break
            await self.bot.say(box(page, lang="py"))

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
