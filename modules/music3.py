from discord.ext import commands 
from discord import opus, ClientException
from ctypes.util import find_library
from utils.Permissions import permissionChecker
from utils.VoiceHandler import ServerVoice


class Music:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.voice = {}

        # Start OPUS if not loaded
        if not opus.is_loaded():
            opus.load_opus(find_library('opus'))

        # Load what VCs it's already in
        for i in self.sparcli.servers:

            # Set up a nice dictionary for storage of information
            voiceClientInServer = self.sparcli.voice_client_in(i)
            self.voice[i] = ServerVoice(bot=self.sparcli, server=i, voiceClient=voiceClientInServer)


    @commands.command(pass_context=True, aliases=['p'])
    async def play(self, ctx, *, nameOfSong:str):
        '''
        Plays a song from a YouTube search or URL.
        '''

        serverHandler = self.voice[ctx.message.server]
        serverHandler.lastChannel = ctx.message.channel
        if serverHandler.voiceClient == None:
            z = await serverHandler.joinVC(ctx.message.author)
            if z == False:
                return
        await serverHandler.addToQueue(nameOfSong)

    @commands.command(pass_context=True, aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        '''
        Makes a bot on the server leave the joined voice channel.
        '''

        serverHandler = self.voice[ctx.message.server]
        serverHandler.lastChannel = ctx.message.channel
        if serverHandler.voiceClient == None:
            await self.sparcli.say('I\'m not currently in a voice channel.')
        else:
            await serverHandler.disconnect()
            await self.sparcli.say('Disconnected from the VC.')

    @commands.command(pass_context=True, aliases=['v'])
    async def volume(self, ctx, volume:int=20):
        '''
        Changes the volume of the currently playing music stream.
        '''

        serverHandler = self.voice[ctx.message.server]
        serverHandler.lastChannel = ctx.message.channel

        z = serverHandler.setVolume(volume)

        await self.sparcli.say('The volume has been set to {}%.'.format(z))

    @commands.command(pass_context=True)
    async def queued(self, ctx):
        '''
        Gets you a list of what is currently queued.
        '''

        serverHandler = self.voice[ctx.message.server]
        serverHandler.lastChannel = ctx.message.channel

        queuedTitles = [i.title for i in serverHandler.queue]
        if len(queuedTitles) > 0:
            out = 'Here is a list of the currently queued items: ```\n{}```'.format('\n'.join(queuedTitles))
        else:
            out = 'There is currently nothing queued to be played :c'
        await self.sparcli.say(out)

    @commands.command(pass_context=True)
    @permissionChecker(check='administrator')
    async def forceskip(self, ctx):
        '''
        Forces the bot to skip to the next song.
        '''

        serverHandler = self.voice[ctx.message.server]
        serverHandler.lastChannel = ctx.message.channel

        if serverHandler.voiceClient == None:
            await self.sparcli.say('I\'m not currently in a voice channel.')
        else:
            await serverHandler.skipChecker(ctx.message, force=True)

    @commands.command(pass_context=True)
    async def musicisfucked(self, ctx):
        '''
        For when the music stops working.
        '''

        i = ctx.message.server

        serverHandler = self.voice[i]
        if serverHandler.voiceClient == None:
            pass
        else:
            await serverHandler.disconnect()

        del self.voice[i]

        voiceClientInServer = self.sparcli.voice_client_in(i)
        self.voice[i] = ServerVoice(bot=self.sparcli, server=i, voiceClient=voiceClientInServer)
        await self.sparcli.say('Done!')

    async def on_reaction_add(self, reaction, user):
        '''
        Checks reactions and etc
        '''

        serverHandler = self.voice[reaction.message.server]
        if serverHandler.songInfoMessage == reaction.message.id:
            await serverHandler.skipChecker(reaction.message)

    async def on_message(self, message):

        # Start the serverhandler looping
        try:
            serverHandler = self.voice[message.server]
        except KeyError:
            i = message.server
            voiceClientInServer = self.sparcli.voice_client_in(i)
            self.voice[i] = ServerVoice(bot=self.sparcli, server=i, voiceClient=voiceClientInServer)
            serverHandler = self.voice[i]

        if serverHandler.looping == False: 
            await serverHandler.loop()

    async def on_server_join(self, server):

        # Make sure the bot knows to add things to its cache when it joins a server
        self.voice[server] = ServerVoice(bot=self.sparcli, server=server, voiceClient=voiceClientInServer)


def setup(bot):
    bot.add_cog(Music(bot))
