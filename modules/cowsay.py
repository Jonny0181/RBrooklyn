import urllib.request
import urllib.error

from discord.ext import commands
import thejoyofpynting


class Paint:
    def __init__(self, bot):
        self.bot = bot

    def cowsay(str, length=40): # https://gist.github.com/wookiecooking/5601887
        bubble = []
    lines  = textwrap.wrap(str, length)
    maxlen = len(max(lines, key=len))
    lines = [ line.ljust(maxlen) for line in lines ]
    bordersize = len(lines[0])
    bubble.append("  " + "_" * bordersize)
    for index, line in enumerate(lines):
        if len(lines) < 2:
            border = [ "<", ">" ]
        elif index == 0:
            border = [ "/", "\\" ]
        elif index == len(lines) - 1:
            border = [ "\\", "/" ]
        else:
            border = [ "|", "|" ]
        bubble.append("%s %s %s" % (border[0], line, border[1]))
    bubble.append("  " + "-" * bordersize)
    okay = "\n".join(bubble) + """
         \   ^__^
          \  (oo)\_______
             (__)\       )\/\\
                 ||----w |
                 ||     ||
    """
    return okay
   


    @commands.command(pass_context=True) # SNED HELP
    async def cowsay(self, ctx, parameters, recursion=0):
        """Return an embed with cowsay [str]."""
        if len(parameters) > 1000:
            await self.bot.say("Sorry {}, too many characters, 1000 max for cowsay!".format(ctx.message.author.mention))
            return
        elif ctx.message.mentions:
            await self.bot.say("Sorry {}, can't use mentions with cowsay!".format(ctx.message.author.mention))
            return
        e = discord.Embed(colour=0x32363B)
        e.set_author(name=str(ctx.message.author)[:-5], icon_url=ctx.message.author.avatar_url)
        output = cowsay(parameters)
        e.description = "```\n"
        e.description += output
        e.description += "\n```"
        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Paint(bot))
