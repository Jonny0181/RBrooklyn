def colourFixer(colour):
    '''Fixes a colour str into hex based on an input'''

    fixColour = colour.replace('#', '')
    for i in fixColour:
        if i.lower() not in '0123456789abcdef':
            fixColour = 'this is a message that will cause an error later'
    if len(fixColour) == 6:
        pass
    elif len(fixColour) == 3:
        fixColour = fixColour * 2
    elif len(fixColour) == 2:
        fixColour = fixColour * 3
    else:
        raise ValueError('The value given was not a valid argument.')
    return fixColour
