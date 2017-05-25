from json import loads, dumps
from os.path import realpath, dirname
from sys import argv
workingDirectory = dirname(realpath(__file__))


def getServerJson(serverID):
    '''
    Returns the JSON config for a server
    '''

    return getWorkingJson('ServerConfigs', serverID)


def saveServerJson(serverID, jsonData):
    '''
    Writes a JSON file into savedata
    '''

    saveWorkingJson('ServerConfigs', serverID, jsonData)


def getMoneyJson(serverID):
    '''
    Returns the JSON config for a server
    '''

    return getWorkingJson('ServerMoney', serverID)


def saveMoneyJson(serverID, jsonData):
    '''
    Writes a JSON file into savedata
    '''

    saveWorkingJson('ServerMoney', serverID, jsonData)


def getWorkingJson(folder, serverID):
    '''
    Returns the JSON config for a server
    '''

    # Try and open a specified file
    try:
        with open(workingDirectory + '/../../{}/{}.json'.format(folder, serverID)) as a:
            jsonData = loads(a.read())

    # The file doesn't exist, load and return the default file data
    except FileNotFoundError:
        with open(workingDirectory + '/../../{}/Default.json'.format(folder)) as a:
            jsonData = loads(a.read())
    return jsonData


def saveWorkingJson(folder, serverID, jsonData):
    '''
    Writes a JSON file into savedata
    '''

    with open(workingDirectory + '/../../{}/{}.json'.format(folder, serverID), 'w') as a:
        a.write(dumps(jsonData, indent=4))


def fixJson(inputDictionary, referenceDictionary=getServerJson('Default')):
    '''
    Fixes an input dictionary with a reference
    '''

    # Go through the reference dictionary
    for i in referenceDictionary:

        # Sees if the different objects exist in the reference
        if type(referenceDictionary[i]) == dict:
            if i not in inputDictionary:
                inputDictionary[i] = referenceDictionary[i]
            else:

                # If it's a JSON, it'll have to reccur through the function
                inputDictionary[i] = fixJson(
                    inputDictionary[i], referenceDictionary[i])
        else:
            if i in inputDictionary:
                pass
            else:
                inputDictionary[i] = referenceDictionary[i]
    return inputDictionary


def getTokens():
    '''
    Gives the arguments passed to the bot through CLI
    '''

    # Get the filename of the tokensheet
    tokenJson = argv[-1]

    # Remove it if it's the bot token
    if tokenJson == argv[1]:
        return False

    # Make sure you get the fileformat
    if tokenJson[-5:] == '.json':
        pass
    else:
        tokenJson = tokenJson + '.json'

    # Parse it as JSON data
    with open(workingDirectory + '/../../{}'.format(tokenJson)) as a:
        tokenReading = loads(a.read())

    # Return it to user
    return tokenReading


def getRedditInstances():
    '''
    Gets all the stored Discord user IDs which are tied to refresh tokens for reddit
    '''

    with open(workingDirectory + '/../../redditInstances.json') as a:
        tokenReading = loads(a.read())

    return tokenReading


def saveRedditInstances(data):
    '''
    Stores some saved reddit instances
    '''
    with open(workingDirectory + '/../../redditInstances.json', 'w') as a:
        a.write(dumps(data, indent=4))
