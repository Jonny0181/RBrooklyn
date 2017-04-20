import discord
from discord.ext import commands

class Info:
	def __init__(self, bot):
		self.bot = bot
		
    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Pong."""
        msg = await self.bot.say("Pinging to server...")
        time = (msg.timestamp - ctx.message.timestamp).total_seconds() * 1000
        await self.bot.edit_message(msg, 'Pong: {}ms :ping_pong:'.format(round(time)))
        
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
        
def setup(bot):
	n = Info(bot)
	bot.add_cog(n)
