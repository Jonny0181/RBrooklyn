import discord
import random
import os
import asyncio
import psutil
import datetime
import time
import copy
from utils.dataIO import dataIO
from discord.ext import commands

starttime = time.time()

class Info:
    def __init__(self, bot):
        self.bot = bot
        self.seen = dataIO.load_json('data/seen/seen.json')
        self.new_data = False

    async def data_writer(self):
        while self == self.bot.get_cog('Seen'):
            if self.new_data:
                dataIO.save_json('data/seen/seen.json', self.seen)
                self.new_data = False
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(30)

    @commands.command(pass_context=True, no_pm=True, name='seen')
    async def _seen(self, context, username: discord.Member):
        '''seen <@username>'''
        server = context.message.server
        author = username
        timestamp_now = context.message.timestamp
        if True if author.id in self.seen[server.id] else False if server.id in self.seen else False:
            data = self.seen[server.id][author.id]
            timestamp_then = datetime.fromtimestamp(data['TIMESTAMP'])
            timestamp = timestamp_now - timestamp_then
            days = timestamp.days
            seconds = timestamp.seconds
            hours = seconds // 3600
            seconds = seconds - (hours * 3600)
            minutes = seconds // 60
            if sum([days, hours, minutes]) < 1:
                ts = 'just now'
            else:
                ts = ''
                if days == 1:
                    ts += '{} day, '.format(days)
                elif days > 1:
                    ts += '{} days, '.format(days)
                if hours == 1:
                    ts += '{} hour, '.format(hours)
                elif hours > 1:
                    ts += '{} hours, '.format(hours)
                if minutes == 1:
                    ts += '{} minute ago'.format(minutes)
                elif minutes > 1:
                    ts += '{} minutes ago'.format(minutes)
            em = discord.Embed(color=discord.Color.green())
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em.set_author(name='{} was seen {}'.format(author.display_name, ts), icon_url=avatar)
            await self.bot.say(embed=em)
        else:
            message = 'I haven\'t seen {} yet.'.format(author.display_name)
            await self.bot.say('{}'.format(message))

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Pong."""
        msg = await self.bot.say("Pinging to server...")
        time = (msg.timestamp - ctx.message.timestamp).total_seconds() * 1000
        await self.bot.edit_message(msg, 'Pong: {}ms :ping_pong:'.format(round(time)))
        
    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Shows stats."""
        text_channels = 0
        voice_channels = 0
        list2 = []
        list = []
        for i in self.bot.servers:
            if i.me.voice_channel is not None:
                list.append(i.me.voice_channel)
        for c in list:
            list2.extend(c.voice_members)
        mem_v = psutil.virtual_memory()
        cpu_p = psutil.cpu_percent(interval=None, percpu=True)
        cpu_usage = sum(cpu_p)/len(cpu_p)
        online = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.online])
        idle = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.idle])
        dnd = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.dnd])
        offline = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.offline])
        seconds = time.time() - starttime
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        t1 = time.perf_counter()
        await self.bot.type()
        t2 = time.perf_counter()
        data = discord.Embed(description="Showing stats for {}.".format(self.bot.user.name), colour=discord.Colour.red())
        data.add_field(name="Owner", value="<@146040787891781632>")
        data.add_field(name="Ping", value="{}ms".format(round((t2-t1)*1000)))
        data.add_field(name="Shard ID", value=self.bot.shard_id)
        data.add_field(name="Shard Count", value=self.bot.shard_count)
        data.add_field(name="Servers", value=len(self.bot.servers))
        data.add_field(name="Api version", value=discord.__version__)
        data.add_field(name="Users", value="{} Online<:vpOnline:212789758110334977>\n{} Idle<:vpAway:212789859071426561>\n{} Dnd<:vpDnD:236744731088912384>\n{} Offline<:vpOffline:212790005943369728>".format(online, idle, dnd, offline))
        data.add_field(name="Channels", value="{} Voice Channels\n{} Text Channels".format(len([e for e in self.bot.get_all_channels() if e.type == discord.ChannelType.voice]), len([e for e in self.bot.get_all_channels() if e.type == discord.ChannelType.text])))
        data.add_field(name='CPU usage', value='{0:.1f}%'.format(cpu_usage))
        data.add_field(name='Memory usage', value='{0:.1f}%'.format(mem_v.percent))
        data.add_field(name="Commands", value="{0} active modules, with {1} commands...".format(len(self.bot.cogs), len(self.bot.commands)))
        data.add_field(name='Uptime', value="%d Weeks," % (w) + " %d Days," % (d) + " %d Hours,"
                                   % (
                h) + " %d Minutes," % (m) + " and %d Seconds!" % (s))
        data.add_field(name="Voice Stats:", value="Connected to {} voice channels, with a total of {} users.".format(len(list), len(list2)), inline=False)
        data.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        data.set_thumbnail(url=ctx.message.author.avatar_url)
        await self.bot.say(embed=data)

    @commands.command(pass_context=True)
    async def mods(self, ctx):
        """Shows mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.online]
        two = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.idle]
        three = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.dnd]
        four = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing mods for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value="{0}".format(("\n".join(one)).replace("`", "")), inline=False)
        else:
            embed.remove_field(0)
        if two:
            embed.add_field(name="Idle", value="{0}".format(("\n".join(two)).replace("`", "")), inline=False)
        else:
            embed.remove_field(1)
        if three:
            embed.add_field(name="Dnd", value="{0}".format(("\n".join(three)).replace("`", "")), inline=False)
        else:
            embed.remove_field(2)
        if four:
            embed.add_field(name="Offline", value="{0}".format(("\n".join(four)).replace("`", "")), inline=False)
        else:
            embed.remove_field(3)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
        
    @commands.command(pass_context=True)
    async def admins(self, ctx):
        """Shows mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.online]
        two = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.idle]
        three = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.dnd]
        four = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing admins for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value="{0}".format(("\n".join(one)).replace("`", "")), inline=False)
        else:
            embed.remove_field(0)
        if two:
            embed.add_field(name="Idle", value="{0}".format(("\n".join(two)).replace("`", "")), inline=False)
        else:
            embed.remove_field(1)
        if three:
            embed.add_field(name="Dnd", value="{0}".format(("\n".join(three)).replace("`", "")), inline=False)
        else:
            embed.remove_field(2)
        if four:
            embed.add_field(name="Offline", value="{0}".format(("\n".join(four)).replace("`", "")), inline=False)
        else:
            embed.remove_field(3)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
        
    @commands.command(pass_context=True)
    async def banlist(self, ctx):
        """Displays the server's banlist"""
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Ban Members` permission")
            return
        bancount = len(banlist)
        if bancount == 0:
            banlist = "No users are banned from this server"
        else:
            banlist = ", ".join(map(str, banlist))
        await self.bot.say("Total bans: `{}`\n```{}```".format(bancount, banlist))
        
    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        "Show server , owner and channel info"
        server = ctx.message.server
        channel = ctx.message.channel
        members = set(server.members)

        owner = server.owner

        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)

        bots = filter(lambda m: m.bot, members)
        bots = set(bots)

        users = members - bots

        msg = '\n'.join((
            'Server Name     : ' + server.name,
            'Server ID       : ' + str(server.id),
            'Server Created  : ' + str(server.created_at),
            'Server Region   : ' + str(server.region),
            'Verification    : ' + str(server.verification_level),
            # minus one for @​everyone
            'Server # Roles  : %i' % (len(server.roles) - 1),
            '',
            'Server Owner    : ' + (
                ('{0.nick} ({0})'.format(owner)) if owner.nick
                else str(owner)),
            'Owner ID        : ' + str(owner.id),
            'Owner Status    : ' + str(owner.status),
            '',
            'Total Bots      : %i' % len(bots),
            'Bots Online     : %i' % len(bots - offline),
            'Bots Offline    : %i' % len(bots & offline),
            '',
            'Total Users     : %i' % len(users),
            'Users Online    : %i' % len(users - offline),
            'Users Offline   : %i' % len(users & offline),
            '',
            'Current Channel : #' + channel.name,
            'Channel ID      : ' + str(channel.id),
            'Channel Created : ' + str(channel.created_at)
        ))
        embed=discord.Embed(description=msg, colour=discord.Colour.blue())
        embed.set_thumbnail(url=ctx.message.server.icon_url)
        await self.bot.say(embed=embed)
        
    def fetch_joined_at(self, user, server):
        return user.joined_at
        
    @commands.command(pass_context=True)
    async def uinfo(self, ctx, *, user: discord.Member=None):
        """Shows userss informations"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "**Playing:** {}".format(user.game)
        else:
            game = "**Streaming:** [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Name", value=user.name)
        data.add_field(name="ID", value=user.id)
        data.add_field(name="Color", value=user.colour)
        data.add_field(name="Discriminator", value=user.discriminator)
        data.add_field(name="VoiceChannel", value=bool(user.voice_channel))
        data.add_field(name="Nickname", value=user.nick)
        data.add_field(name="Deafened", value="Local: {}\nServer: {}".format(user.self_deaf, user.deaf))
        data.add_field(name="Muted", value="Local: {}\nServer: {}".format(user.self_mute, user.mute))
        data.add_field(name="Status", value=user.status)
        data.add_field(name="Top Role", value=user.top_role)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="All Roles", value=roles, inline=False)
        data.set_footer(text="Member Number: {}"
                             "".format(member_number))
        if user.avatar_url:
            name = str(user)
            name = " ~ ".join((name, user.nick)) if user.nick else name
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=user.name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            author = ctx.message.author
            server = ctx.message.server
            if not user:
                user = author
            roles = [x.name for x in user.roles if x.name != "@everyone"]
            if not roles: roles = ["None"]
            data = "```prolog\n"
            data += "Name: {}\n".format(str(user))
            data += "Nickname: {}\n".format(str(user.nick))
            data += "ID: {}\n".format(user.id)
            if user.game is None:
                pass
            elif user.game.url is None:
                data += "Playing: {}\n".format(str(user.game))
            else:
                data += "Streaming: {} ({})\n".format(str(user.game),(user.game.url))
            passed = (ctx.message.timestamp - user.created_at).days
            data += "Created: {} ({} days ago)\n".format(user.created_at, passed)
            joined_at = self.fetch_joined_at(user, server)
            passed = (ctx.message.timestamp - joined_at).days
            data += "Joined: {} ({} days ago)\n".format(joined_at, passed)
            data += "Roles: {}\n".format(", ".join(roles))
            if user.avatar_url != "":
                data += "Avatar:"
                data += "```"
                data += user.avatar_url
            else:
                data += "```"
            await self.bot.say(data)
            
    @commands.command(pass_context=True)
    async def emotes(self, ctx):
        """Server emotes."""
        server = ctx.message.server

        list = [e for e in server.emojis if not e.managed]
        emoji = ''
        for emote in list:
            emoji += "<:{0.name}:{0.id}> ".format(emote)
        try:
            await self.bot.say(emoji)
        except:
            await self.bot.say("Server has no emotes.")
            
    @commands.command(pass_context=True)
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Retrieves a users avatar."""
        author = ctx.message.author
        if not user:
            user = author
        data = discord.Embed(colour=user.colour)
        data.set_image(url=user.avatar_url)
        data.set_author(name="Avatar for "+user.name, icon_url=user.avatar_url)
        data.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.say(embed=data)
        
    @commands.command(pass_context=True)
    async def permissions(self, ctx):
        user = await self._prompt(ctx, "Mention a user...")
        try:
            if user.mentions is not None:
                user = user.mentions[0]
        except:
            try:
                user = discord.utils.get(ctx.message.server.members, name=str(user.content))
            except:
                return await self.bot.say("User not found!:x:")
        perms = iter(ctx.message.channel.permissions_for(user))
        perms_we_have = "```diff\n"
        perms_we_dont = ""
        for x in perms:
            if "True" in str(x):
                perms_we_have += "+\t{0}\n".format(str(x).split('\'')[1])
            else:
                perms_we_dont += ("-\t{0}\n".format(str(x).split('\'')[1]))
        await self.bot.say("{0}{1}```".format(perms_we_have, perms_we_dont))

    async def _prompt(self, ctx, msg: str):
        await self.bot.say(msg)
        msg = await self.bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        return msg
        
    async def on_message(self, message):
        if not message.channel.is_private and self.bot.user.id != message.author.id:
            if not any(message.content.startswith(n) for n in self.bot.settings.prefixes):
                server = message.server
                author = message.author
                ts = message.timestamp.timestamp()
                data = {}
                data['TIMESTAMP'] = ts
                if server.id not in self.seen:
                    self.seen[server.id] = {}
                self.seen[server.id][author.id] = data
                self.new_data = True


def check_folder():
    if not os.path.exists('data/seen'):
        print('Creating data/seen folder...')
        os.makedirs('data/seen')


def check_file():
    data = {}
    data['db_version'] = DB_VERSION
    f = 'data/seen/seen.json'
    if not dataIO.is_valid_json(f):
        print('Creating seen.json...')
        dataIO.save_json(f, data)
    else:
        check = dataIO.load_json(f)
        if 'db_version' in check:
            if check['db_version'] < DB_VERSION:
                data = {}
                data['db_version'] = DB_VERSION
                dataIO.save_json(f, data)
                print('SEEN: Database version too old, resetting!')
        else:
            data = {}
            data['db_version'] = DB_VERSION
            dataIO.save_json(f, data)
            print('SEEN: Database version too old, resetting!')


def setup(bot):
    check_folder()
    check_file()
    n = Info(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.data_writer())
    bot.add_cog(n)
