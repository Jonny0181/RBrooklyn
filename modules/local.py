import discord
from discord.ext import commands
import os

class NotConnected(Exception):
    pass

class AuthorNotConnected(NotConnected):
    pass

class UnauthorizedConnect(Exception):
    pass

class UnauthorizedSpeak(Exception):
    pass

class ChannelUserLimit(Exception):
    pass

class Local:
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.local_playlist_path = "data/audio/localtracks"

    def voice_connected(self, server):
        if self.bot.is_voice_connected(server):
            return True
        return False

    def has_connect_perm(self, author, server):
        channel = author.voice_channel

        if channel:
            is_admin = channel.permissions_for(server.me).administrator
            if channel.user_limit == 0:
                is_full = False
            else:
                is_full = len(channel.voice_members) >= channel.user_limit

        if channel is None:
            raise AuthorNotConnected
        elif channel.permissions_for(server.me).connect is False:
            raise UnauthorizedConnect
        elif channel.permissions_for(server.me).speak is False:
            raise UnauthorizedSpeak
        elif is_full and not is_admin:
            raise ChannelUserLimit
        else:
            return True
        return False

    def _setup_queue(self, server):
        self.queue[server.id] = {"REPEAT": False, "PLAYLIST": False,
                                 "VOICE_CHANNEL_ID": None,
                                 "QUEUE": deque(), "TEMP_QUEUE": deque(),
                                 "NOW_PLAYING": None}

    def _play_playlist(self, server, playlist):
        try:
            songlist = playlist.playlist
            name = playlist.name
        except AttributeError:
            songlist = playlist
            name = True

        log.debug("setting up playlist {} on sid {}".format(name, server.id))

        self._stop_player(server)
        self._stop_downloader(server)
        self._clear_queue(server)

        log.debug("finished resetting state on sid {}".format(server.id))

        self._setup_queue(server)
        self._set_queue_playlist(server, name)
        self._set_queue_repeat(server, True)
        self._set_queue(server, songlist)

    def _set_queue(self, server, songlist):
        if server.id in self.queue:
            self._clear_queue(server)
        else:
            self._setup_queue(server)
        self.queue[server.id]["QUEUE"].extend(songlist)

    def _set_queue_repeat(self, server, value):
        if server.id not in self.queue:
            self._setup_queue(server)

        self.queue[server.id]["REPEAT"] = value

    def _set_queue_playlist(self, server, name=True):
        if server.id not in self.queue:
            self._setup_queue(server)

        self.queue[server.id]["PLAYLIST"] = name

    def _play_local_playlist(self, server, name):
        songlist = self._local_playlist_songlist(name)

        ret = []
        for song in songlist:
            ret.append(os.path.join(name, song))

        ret_playlist = Playlist(server=server, name=name, playlist=ret)
        self._play_playlist(server, ret_playlist)

    @commands.group(pass_context=True, no_pm=True)
    async def local(self, ctx):
        """Local playlists commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            
    @local.command(name="start", pass_context=True, no_pm=True)
    async def play_local(self, ctx, *, name):
        """Plays a local playlist"""
        server = ctx.message.server
        author = ctx.message.author
        voice_channel = author.voice_channel

        # Checking already connected, will join if not

        if not self.voice_connected(server):
            try:
                self.has_connect_perm(author, server)
            except AuthorNotConnected:
                await self.bot.say("You must join a voice channel before I can"
                                   " play anything.")
                return
            except UnauthorizedConnect:
                await self.bot.say("I don't have permissions to join your"
                                   " voice channel.")
                return
            except UnauthorizedSpeak:
                await self.bot.say("I don't have permissions to speak in your"
                                   " voice channel.")
                return
            except ChannelUserLimit:
                await self.bot.say("Your voice channel is full.")
                return
            else:
                await self._join_voice_channel(voice_channel)
        else:  # We are connected but not to the right channel
            if self.voice_client(server).channel != voice_channel:
                pass

        lists = self._list_local_playlists()

        if not any(map(lambda l: os.path.split(l)[1] == name, lists)):
            await self.bot.say("Local playlist not found.")
            return

        self._play_local_playlist(server, name)

    @local.command(name="list", no_pm=True)
    async def list_local(self):
        """Lists local playlists"""
        playlists = ", ".join(self._list_local_playlists())
        if playlists:
            playlists = "Available local playlists:\n\n" + playlists
            for page in pagify(playlists, delims=[" "]):
                await self.bot.say(page)
        else:
            await self.bot.say("There are no playlists.")

def check_folders():
    folders = ("data/audio/localtracks")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)
            
def setup(bot):
    check_folders()
    n = Local(bot)
    bot.add_cog(n)
