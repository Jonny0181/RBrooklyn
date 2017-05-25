from discord.ext import commands
from .Configs import getTokens
from .Exceptions import *


def needsToken(**kwargs):
    '''Checks to see if a certain token type's secret exists
    Parameters :: 
        token : str
            The type of token whose secret needs to exist
    '''

    def predicate(ctx):
        token = kwargs.get('token', None)

        if getTokens()[token]['Secret'] == '':
            raise ThisNeedsAToken
        return True
        
    return commands.check(predicate)


def permissionChecker(**kwargs):
    '''Checks permissions based on ctx and some kwargs
    Parameters :: 
        check : str
            The permssion check that the bot will look for
        compare : bool = None
            The type of tag that the bot will look to compare against
            Defaults to None, and will just return whether or not the user has permission
        owners : list (of str)
            Lets the bot add additional owners to just a command
    '''

    def predicate(ctx):
        check = kwargs.get('check', 'send_messages')
        compare = kwargs.get('compare', False)
        owners = kwargs.get('owners', [])
        channel = ctx.message.channel
        server = ctx.message.server 
        author = ctx.message.author
        tokens = getTokens()

        # Checks if it's an owner
        if author.id in tokens['OwnerIDs'] + owners:
            return True
        elif check == 'is_owner':
            raise MemberMissingPermissions
            return False

        # Checks if it's a PM
        if server == None:
            # Handle PM'd messages better later, for now just say you can't do them
            raise DoesntWorkInPrivate
            return False

        # Sees if the author is the server owner
        if server.owner.id == author.id:
            return True

        # Looks at the person to compare against
        if compare == True:

            # Get the member mentions in the message (excluding the bot)
            mentions = [i for i in ctx.message.mentions if i.id != tokens['BotID']]

            # Check that it's not empty
            if mentions == []: 
                raise MemberPermissionsTooLow
                return False

            # Pretty much just return false if they have a higher top role, otherwise continue
            if author.top_role.position <= mentions[-1].top_role.position: 
                raise MemberPermissionsTooLow
                return False

        # Check that the user has permission to actually do what they want to
        permissionsInChannel = channel.permissions_for(author)
        if getattr(permissionsInChannel, 'administrator'):
            return True
        z = getattr(permissionsInChannel, check)
        if z:
            return z
        else:
            raise MemberMissingPermissions
            return False

    return commands.check(predicate)


def botPermission(**kwargs):
    '''Checks that the bot actually has permission to do what it's trying to do
    It makes sure its own highest role (on the message's server) is higher than
    the tagged member that's in the message
    Parameters ::
        check : str
            Should be the thing that the bot is trying to do
            eg: check='ban_members'
        compare : bool
            Whether to compare the bot's top role to a tagged user's
    '''

    def predicate(ctx):
        check = kwargs.get('check', 'send_messages')
        compare = kwargs.get('compare', False)
        botMember = ctx.message.server.me 
        tokens = getTokens()
        mentions = [i for i in ctx.message.mentions if i.id != tokens['BotID']]
        perms = ctx.message.channel.permissions_for(botMember)

        # Check the bot's permissions
        if compare == False:
            # No comparison, just say whether the bot can do it
            x = getattr(perms, check)
            if x == True:
                return x
            raise BotMissingPermissions
        elif getattr(perms, check) == False:
            # Compare, but the bot can't run the command
            raise BotMissingPermissions
            return False 
        else:
            # The bot has permission to run the command, now checking if can be run on the
            # tagged member
            pass

        # Makes sure that there actually are mentions
        if mentions == []:
            user = ctx.message.author
        else:
            user = mentions[0]

        x = botMember.top_role.position > user.top_role.position
        if x == True:
            return True
        else:
            raise BotPermissionsTooLow
            return False

    return commands.check(predicate)
