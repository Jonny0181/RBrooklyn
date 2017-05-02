import os
import discord
import asyncio
from utils import checks
from discord.ext import commands
from utils.dataIO import dataIO

class Mod:
    def __init__(self, bot):
        self.bot = bot
        self._tmp_banned_cache = []
        self.settings = dataIO.load_json("data/warner/warnings.json")
        
    def delete_mine(self,m):
        return m.author.id == self.bot.user.id

    @commands.command(pass_context=True)
    @commands.check(check_roles)
    async def clean(self, ctx, *, limit:int=100):
        """Allows the bot to delete his own messages"""
        counter = await ctx.message.channel.purge(limit = limit,check=self.delete_mine)
        msg = await self.bot.say("```py\nCleaned up messages: {}\n```".format(len(counter)))
        await asyncio.sleep(2)
        await self.bot.delete_message(msg)

    @commands.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def warn(self, ctx, user:discord.Member, times:int=1):
        """Warn people for their actions."""
        serverid = ctx.message.server.id
        userid = user.id
        if serverid not in self.settings:
            self.settings[serverid] = {}
            self.save_settings()
        if userid not in self.settings[serverid]:
            self.settings[serverid][userid] = 1
            self.save_settings()
            await self.bot.say("The user has 1 warnings but nothing happens yet, next up: 5 minute mute.")
            return
        else:
            self.settings[serverid][userid] += times
            self.save_settings()
            if self.settings[serverid][userid] == 1:
                await self.bot.say("The user has 1 warnings but nothing happens yet, next up: 5 minute mute.")
            if self.settings[serverid][userid] == 2:
                await self.bot.say("The user has 2 warnings and has been muted for 5 minutes, next up: 30 minute mute.")
                await self.mute(user, 5)
            elif self.settings[serverid][userid] == 3:
                await self.bot.say("The user has 3 warnings and has been muted for 30 minutes, next up: kick.")
                await self.mute(user, 30)
            elif self.settings[serverid][userid] == 4:
                try:
                    await self.bot.kick(user)
                    await self.bot.say("The user has 4 warnings and has been kicked, next up: ban.")
                except discord.Forbidden:
                    await self.bot.say("The user has 4 warnings but could not be kicked because I do not have the right perms for that.")
                except:
                    await self.bot.say("The user has 4 warnings but an unknown error occured while trying to kick the user.")
            elif self.settings[serverid][userid] >= 5:
                try:
                    await self.bot.ban(user, delete_message_days=3)
                    del self.settings[serverid][userid]
                    self.save_settings()
                    await self.bot.say("The user has 5 warnings and has been banned.")
                except discord.Forbidden:
                    await self.bot.say("The user has 5 warnings but could not be banned because I do not have the right perms for that.")
                except:
                    await self.bot.say("The user has 5 warnings but an unknown error occured while trying to ban the user.")
                
    @commands.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def resetwarns(self, ctx, user:discord.Member):
        """Reset the warnings you gave to someone"""
        serverid = ctx.message.server.id
        userid = user.id
        if serverid not in self.settings:
            await self.bot.say("No one in this server has got a warning yet.")
            return
        elif userid not in self.settings[serverid]:
            await self.bot.say("This user doesn't have a warning yet.")
            return
        else:
            del self.settings[serverid][userid]
            self.save_settings()
            await self.bot.say("Users warnings succesfully reset!")
            return
            
    @commands.command(pass_context=True, no_pm=True)
    async def warns(self, ctx, user:discord.Member):
        """See how much warnings someone has."""
        if ctx.message.server.id not in self.settings:
            await self.bot.say("No one in this server has got a warning yet.")
            return
        elif user.id not in self.settings[ctx.message.server.id]:
            await self.bot.say("This user doesn't have a warning yet.")
            return
        elif self.settings[ctx.message.server.id][user.id] == 1:
            await self.bot.say("This user has {} warning.".format(self.settings[ctx.message.server.id][user.id]))
            return
        else:
            await self.bot.say("This user has {} warnings.".format(self.settings[ctx.message.server.id][user.id]))
            
    def save_settings(self):
        dataIO.save_json("data/warner/warnings.json", self.settings)
            
    async def mute(self, member, minutes:int):
        for channel in member.server.channels:
            perms = discord.PermissionOverwrite()
            perms.send_messages = False
            await self.bot.edit_channel_permissions(channel, member, perms)
        await asyncio.sleep(minutes * 60)
        for channel in member.server.channels:
            perms = discord.PermissionOverwrite()
            perms.send_messages = None
            await self.bot.edit_channel_permissions(channel, member, perms)
        
    @commands.command(pass_context = True)
    @checks.botcom()
    async def botclean(self, ctx, limit : int = None):
        """Removes all bot messages."""
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await self.bot.purge_from(ctx.message.channel, limit=limit, before=ctx.message, check= lambda e: e.author.bot)

    @commands.command(pass_context=True)
    @checks.botcom()
    async def unban(self, ctx, *, user_id: str):
        """Unbans users by ID."""

        server = ctx.message.server.id
        try:
            await self.bot.http.unban(user_id, server)
            await self.bot.say("User unbanned, was <@{}>.".format(user_id))
        except:
            await self.bot.say("Failed to unban. Either `Lacking Permissions` or `User cannot be found`.")

    @commands.command(pass_context=True)
    @checks.botcom()
    async def hackban(self, ctx, *, user_id: str):
        """Bans users by ID.
        This method does not require the user to be on the server."""

        server = ctx.message.server.id
        try:
            await self.bot.http.ban(user_id, server)
            await self.bot.say("User banned, was <@{}>.".format(user_id))
        except:
            await self.bot.say("Failed to ban. Either `Lacking Permissions` or `User cannot be found`.")

    @commands.command(no_pm=True, pass_context=True)
    @checks.botcom()
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
    @checks.botcom()
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
    @checks.botcom()
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

    @prune.command(pass_context=True)
    async def role(self,ctx,roles : discord.Role,limit : int=100):
        """Is able to prune messages of all users who have a certain role."""
        def delete_role(m):
            print(m.author)
            return roles.id in [r.id for r in m.author.roles]
        counter =await ctx.message.channel.purge(limit=limit,check=delete_role)
        msg = await self.bot.say("\nCleaned up messages: {} from {}!".format(len(counter),roles.name))
        await asyncio.sleep(2)
        await self.bot.delete_message(msg)

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

def check_folders():
    if not os.path.exists("data/warner"):
        print("Creating data/warner folder...")
        os.makedirs("data/warner")

def check_files():
    if not os.path.exists("data/warner/warnings.json"):
        print("Creating data/warner/warnings.json file...")
        dataIO.save_json("data/warner/warnings.json", {})
                
def setup(bot):
    check_folders()
    check_files()
    n = Mod(bot)
    bot.add_cog(n)
