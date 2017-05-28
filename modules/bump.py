import discord
import asyncio
from discord.ext import commands

class bump:
    """Bump!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 1500, type=commands.BucketType.server)
    @commands.command(pass_context=True)
    async def bump(self, ctx):
        """Bump your server!"""
        if "bumpchannel" not in self.path or not self.path["bumpchannel"]:
            await self.bot.say("No channel has been set for bump messages to go to!")
            return
        inv = await self.bot.create_invite(ctx.message.server)
        server = ctx.message.server
        count = 1
        channels = [r for s in bot.servers for r in s.channels if r.name == "brooklyn_bump"]
        if not channel:
            await self.bot.say("Something went wrong with getting the channels!")
            return
        em = discord.Embed(title= "{}".format(server.name), color=0xFFFFFF, description="""
**Server Information**
:black_small_square: Server Owner : {}
:black_small_square: Member Count : {}
""".format(server.owner, server.member_count)) #0x0BFCF2 is the color code
        em.add_field(name='**Description**', value="""
:black_small_square: {}""".format(server.default_channel.topic))
        em.add_field(name='**Server Invite**', value="""
:black_small_square: {}""".format(inv))
        em.set_thumbnail(url=server.icon_url) #Or insert actual URL
        for channel in channels:
            await self.bot.send_message(channel, embed=em)
        server = ctx.message.server
        des = server.default_channel.topic
        members = server.member_count
        inv = await self.bot.create_invite(ctx.message.server)
        message = "Server: {0} \n Description: {1} \n Users: {2} \n  Invite: {3}".format(server, des, members, inv)
        self.bot.send_message(channel, embed=em)
        end = discord.Embed(title="Your Server Was Succesfully Bumped", description=message, colour=discord.Colour.green())
        await self.bot.say(embed=end)
    
def setup(bot):
    bot.add_cog(bump(bot))
