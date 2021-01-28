"""
deckimage.py
Contains utility functions for deckimage_bot.py
"""

import cairosvg
import ast

#Getting deck images
def get_deck_png(deckcode, height=240):
    """
    Arguments:
        deckcode (str): the deck code
    Returns
        bytestring of the png data of the deck image
    """
    return cairosvg.svg2png(url="https://etg.dek.im/deck/{}.svg".format(deckcode), output_height=height)
    
#Using the above, saves to a file; for testing purposes
def save_deck_png(deckcode, filename):
    png = get_deck_png(deckcode)
    
    with open(filename, 'wb') as file:
        file.write(png)
    
#For channel settings
def load_channel_data(filename):
    with open(filename, 'r') as file:
        s = file.read()
        serverdict = ast.literal_eval(s)
        if serverdict == dict(serverdict):
            return serverdict
        else:
            return None
    return None
        
def write_channel_data(filename, serverdict):
    with open(filename, 'w') as file:
        file.write(repr(serverdict))

#Load the settings file
def load_settings(filename):
    """
    Loads the settings file into a dictionary
    """
    settings = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#' or line.count('=') != 1:
                continue
            split = line.split('=')
            settings[split[0]] = split[1]
        return settings