from discord import Channel, ClientException
from string import punctuation as AllPunctuation
from asyncio import sleep
from datetime import timedelta
from collections import OrderedDict
from .Messages import makeEmbed


class ServerVoice(object):
    '''
    A handler for the voice client on a server
    '''

    working = False

    def __init__(self, bot, **kwargs):
        self.sparcli = bot
        self.lastChannel = kwargs.get('lastChannel', kwargs['server'])
        self.queue = kwargs.get('queue', [])
        self.forceNext = False
        self.voiceClient = kwargs.get('voiceClient', None)
        self.streamClient = kwargs.get('streamClient', None)
        self.volume = kwargs.get('volume', 0.2)
        self.looping = False
        self.songInfoMessage = None

    async def joinVC(self, toJoin, channel=None):
        '''
        Joins a given voice channel.
        Will join the VC of a member if a member is passed.
        '''

        if channel == None:
            channel = self.lastChannel

        # Join a channel if specified
        if type(toJoin) == Channel:
            loadedVC = self.sparcli.join_voice_channel(toJoin)
            self.voiceClient = loadedVC
            return loadedVC

        # No channel specified, join the user's VC
        memberVC = toJoin.voice.voice_channel
        if memberVC == None:
            await self.sparcli.send_message(channel, 'You aren\'t currently in a voice channel.')
            return False

        # Join the member's VC
        try:
            # Try to join
            loadedVC = await self.sparcli.join_voice_channel(memberVC)
            self.voiceClient = loadedVC
            return loadedVC

        except ClientException:
            # You're already in it
            loadedVC = self.sparcli.voice_client_in(toJoin.server)
            self.voiceClient = loadedVC
            return loadedVC

        else:
            # You can't join it
            await self.sparcli.send_message(channel, 'I am unable to join that voice channel.')
            return False

    def handleBlacklist(self, streamClient):
        '''
        Sets a blacklist for certain terms - earrape, etc.
        '''

        # Get the song title
        title = streamClient.title

        # Sets up the blacklist
        blacklistedTerms = [
            'ear rape',
            'earrape',
            'rip headphone',
            'ripheadphone',
            'thomas the pain train',
            'thomas the pain',
            'pain train'
        ]

        # Make check if it can filter through
        c = [i.lower() in title.lower() for i in blacklistedTerms]
        if True in c:
            return blacklistedTerms[c.index(True)]

        # It *should* be fine I think
        return True

    async def createPlayer(self, songName, channel=None):
        '''
        Creates a YTDL player for a given searchterm.
        '''

        if channel == None:
            channel = self.lastChannel

        # Make sure it filters through ytdl properly
        if 'http://' in songName.lower() or 'https://' in songName.lower():
            searchTerm = songName
        else:
            searchTerm = 'ytsearch:' + songName

        voiceClient = self.voiceClient
        
        # Create the streamclient
        try:
            while ServerVoice.working:
                await sleep(0.1)
            ServerVoice.working = True
            streamClient = await voiceClient.create_ytdl_player(searchTerm)
            ServerVoice.working = False

        except Exception as e:           
           # Could not create the stream client
           await self.sparcli.send_message(channel, 'I was unable to find an applicable YouTube video for the search term `{}`.'.format(songName))
           await self.sparcli.send_message(channel, e + str(e))
           return None

        # Check the blacklist for the thinamawhatsit
        c = self.handleBlacklist(streamClient)
        if c is not True:
            await self.sparcli.send_message(channel, 'Your search term\'s first result returns a video with a blacklisted title (`{.title}`, matching `{}`).'.format(streamClient, c))
            return None

        return streamClient

    async def startPlayer(self, player):
        '''
        Starts a player and sets it to the streamClient attribute.
        '''

        # Stop current stream
        try: self.streamClient.stop()
        except AttributeError: pass

        # Start next one
        player.volume = self.volume
        player.start()
        self.streamClient = player

        # Print out to user
        await self.playEmbed(player)

    async def skipChecker(self, message, force=False, channel=None):
        '''
        Adds one to the skip counter.
        '''

        if channel == None:
            channel = self.lastChannel

        emoji = [[str(i.emoji), i.count] for i in message.reactions]
        if ['⏭', 4] in emoji or force:
            await self.sparcli.send_message(channel, 'This song has received enough vote skips to go to the next song. Skipping...')
            
            try:
                self.songInfoMessage = None
                await self.startPlayer(self.queue[0])
                del self.queue[0]
            except IndexError:
                self.songInfoMessage = None
                self.streamClient.stop()

    async def playEmbed(self, player, channel=None):
        '''
        Creates and sends an embed based on the steamclient.
        '''

        if channel == None:
            channel = self.lastChannel

        title = player.title
        duration = timedelta(seconds=player.duration)
        description = player.description
        likes = player.likes
        dislikes = player.dislikes
        views = player.views
        uploader = player.uploader
        date = player.upload_date

        if len(description) > 100:
            d = description.split(' ')
            f = []
            while len(' '.join(f)) < 100:
                f.append(d[0])
                del d[0]
            g = ' '.join(f)
            fdesc = g if g == description else g + '...'
            if fdesc[-3:] == '...':
                if fdesc[-4] in AllPunctuation: 
                    fdesc = fdesc[:-4] + '...'
        else:
            fdesc = description

        o = OrderedDict()
        o['Title'] = (title, False)
        o['Views'] = views 
        o['Duration'] = duration 
        o['Uploader'] = uploader 
        o['Upload Date'] = date
        o['Likes'] = likes 
        o['Dislikes'] = dislikes 
        o['Description'] = (fdesc, False)

        if o['Description'][0] == '':
            del o['Description']

        e = makeEmbed(author='Now Playing!', fields=o, user=self.sparcli.user)
        q = await self.sparcli.send_message(channel, 'React with ⏭ to vote skip. 3 votes (4 reactions) are required.', embed=e)
        await self.sparcli.add_reaction(q, '⏭')
        self.songInfoMessage = q.id

    async def addToQueue(self, whatToAdd, channel=None):
        '''
        Adds an item to the queue of the VC.
        '''

        if channel == None:
            channel = self.lastChannel

        q = await self.createPlayer(whatToAdd)
        if q == None: return
        self.queue.append(q)
        if self.queue != [q]:
            await self.sparcli.send_message(channel, 'The video `{.title}` has been added to the queue.'.format(q))

    async def disconnect(self):
        '''
        Disconnects the voice client from any voice channel.
        '''

        try:
            self.streamClient.stop()
        except AttributeError:
            pass

        # Leave the voice channel
        await self.voiceClient.disconnect()

        self.queue = []
        self.voiceClient = None
        self.streamClient = None

    def setVolume(self, amount:int):
        '''
        Changes the volume level.
        '''

        if amount > 100: amount = 100
        if amount < 0: amount = 0
        percentage = amount/100.0

        try:
            self.streamClient.volume = percentage
        except AttributeError:
            pass

        self.volume = percentage
        return amount

    async def loop(self):
        '''
        Defines the looping segment that constantly checks the queue for songs to play
        '''

        doPlayNext = True
        self.looping = True

        while True:

            # Check if the queue is empty
            if len(self.queue) > 0:

                # It's not, so check if playing anything currently
                try:

                    # It isn't playing
                    if self.streamClient.is_done():
                        doPlayNext = True

                    # It is playing
                    else:
                        doPlayNext = False

                # No current client
                except Exception:
                    doPlayNext = True

            # Play the next thing in the queue
            if doPlayNext and len(self.queue) > 0:
                await self.startPlayer(self.queue[0])
                del self.queue[0]

            # Now sleep
            await sleep(3)
