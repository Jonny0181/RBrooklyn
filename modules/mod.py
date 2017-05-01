import discord
from discord.ext import commands

class Mod:
    def __init__(self, bot):
        self.bot = bot
        self._tmp_banned_cache = []
        
    @commands.command(pass_context = True)
    @checks.mod_or_permissions(manage_messages=True)
    async def botclean(self, ctx, limit : int = None):
        """Removes all bot messages."""
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await self.bot.purge_from(ctx.message.channel, limit=limit, before=ctx.message, check= lambda e: e.author.bot)

    @commands.command(no_pm=True, pass_context=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str=None):
        """Bans a user from the server."""
        author = ctx.message.author
        server = author.server
        channel = ctx.message.channel
        can_ban = channel.permissions_for(server.me).ban_members
        if can_ban:
            try:  # We don't want blocked DMs preventing us from banning
                await self.bot.send_message(user, "**You have been banned from {}.**\n**Reason:**  {}".format(server.name, reason))
                pass
                await self.bot.ban(user)
                await self.bot.say("Done, I have banned {} from the server.".format(user.name))
            except discord.errors.Forbidden:
                await self.bot.say("I do not have the perms to ban users in this chat, please give ban perms.")
            except Exception as e:
                print(e)
                
    @commands.command(no_pm=True, pass_context=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str=None):
        """Kicks user."""
        author = ctx.message.author
        server = author.server
        try:
            await self.bot.send_message(user, "**You have been kicked from {}.**\n**Reason:**  {}".format(server.name, reason))
            await self.bot.kick(user)
            await self.bot.say("Done, I have kicked {} from the server.".format(user.name))
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the perms to kick users in this chat, please give kick perms.")
        except Exception as e:
            print(e)

    @commands.group(pass_context=True)
    async def prune(self, ctx, number: int):
        """Deletes messages."""
        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return

        async for message in self.bot.logs_from(channel, limit=number+1):
            to_delete.append(message)

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.bot.delete_message(messages[0])
                messages = []
            await asyncio.sleep(1.5)

    async def slow_deletion(self, messages):
        for message in messages:
            try:
                await self.bot.delete_message(message)
            except:
                pass



                
def setup(bot):
	n = Mod(bot)
	bot.add_cog(n)
