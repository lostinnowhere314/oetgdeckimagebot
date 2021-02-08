#deckimage_bot.py
"""
Deck image discord bot
19. January 2021
by Lost in Nowhere
"""

import discord
import re
import io
import deckimage_utils as utils

class deck_client(discord.Client):
    """
    Class for a oEtG deckimage posting discord bot
    
    Attributes:
        server_settings - dict containing data on which channels are set to have deck posting enabled.
            Server ids are used as keys, and mapped to a set of channels (indexed by name string) in which the deck poster is enabled.
        deck_regex - regular expression used to find deck codes in posted messages
        max_decks - the maximum number of decks the bot will extract from a single post. -1 for unlimited.
    """
    
    def __init__(self, settings_file):
        super().__init__()
        
        #Load the settings
        settings = utils.load_settings(settings_file)
        TOKEN = settings['DISCORD_TOKEN']
        self.max_decks=int(settings['MAX_DECK_POST'])
        self.border_color=int(settings['BORDER_COLOR'], base=16)
        
        #Regex for searching messages for deck codes, also attempting to make sure they aren't just a random string that isn't a deck code
        self.deck_regex = r"(?:\s|\A|(?:deck\.htm#)|(?:deck\/))((?:[01][0-9a-v](?<!00)[0-9a-v]{3}){3,})(?:\Z|(?![0-9a-zA-Z]))"
        
        #Try loading server settings
        self.server_settings = utils.load_channel_data("servers.dat")
        if self.server_settings is None:
            self.server_settings = dict()

        print("Connecting...")
        self.run(TOKEN)
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
        for guild in self.guilds:
            print(guild.name)
    
    async def on_message(self, message):
        """
        Check for commands and deck codes in newly posted messages
        """
        #Don't do anything for posts that the bot makes
        if message.author == self.user:
            return
            
        #check for commands
        if message.clean_content.startswith("!deck"):
            if self.can_user_set(message.author, message.channel):
                await self.process_command(message)
            return
        
        #check that the channel of the message is enabled for deck posting
        if not self.is_channel_enabled(message.guild.id, message.channel.name):
            return
        
        #Check for deck codes
        codes = [match.group(1) for match in re.finditer(self.deck_regex, message.clean_content)]
        
        if len(codes) > 0:
            #Process up to three 
            try:
                for code in codes[:self.max_decks]:
                    deck_image = utils.get_deck_png(code, height=186)
                    
                    #Upload as an embedded image
                    file = discord.File(io.BytesIO(deck_image), "deck.png")
                    #embed = discord.Embed()
                    embed = discord.Embed(title="https://etg.dek.im/deck.htm#{}".format(code), color=self.border_color)
                    embed.set_image(url="attachment://image.png")
                    await message.channel.send(file=file, embed=embed)
                    
            except Exception as e:
                print(str(e))
    
    #TODO
    async def process_command(self, message):
        """
        Evaluates commands.
        """
        command = message.clean_content.strip()
        if command == '!deck help':
            await message.channel.send("""The following commands are available:
``!deck help - Displays this info
!deck enable - Enables deck image posting in the current channel
!deck disable - Disables deck image posting in the current channel
!deck enable/disable all - Enables or disables deck posting to all channels in this server``
Only users with the `manage channels` permission may use these commands.""")
            
        elif command == '!deck enable':
            self.set_channel_enabled(message.guild.id, message.channel.name, True)
            await message.channel.send("Deck image posting enabled in this channel.")
            
        elif command == '!deck disable':
            self.set_channel_enabled(message.guild.id, message.channel.name, False)
            await message.channel.send("Deck image posting disabled in this channel.")
            
        elif command == '!deck enable all':
            for channel in message.guild.channels:
                if channel.type == discord.ChannelType.text:
                    self.set_channel_enabled(message.guild.id, channel.name, True)
            await message.channel.send("Deck image posting enabled in all channels.")
            
        elif command == '!deck disable all':
            for channel in message.guild.channels:
                if channel.type == discord.ChannelType.text:
                    self.set_channel_enabled(message.guild.id, channel.name, False)
            await message.channel.send("Deck image posting disabled in all channels.")
            
        else:
            await message.channel.send("Command not recognized. Use `!deck help` to display available commands.")
        
    def is_channel_enabled(self, guild_id, channel_name):
        """
        Checks if the channel in the given server is enabled for deck posting
        """
        if guild_id in self.server_settings.keys():
            return channel_name in self.server_settings[guild_id]
        else:
            return False
    
    def set_channel_enabled(self, guild_id, channel_name, enable):
        """
        Sets whether deck posting is enabled in the given channel on the server
        """
        #Add the server name to the dict if it doesn't exist yet
        if not guild_id in self.server_settings.keys():
            self.server_settings[guild_id] = set()
            
        if enable:
            self.server_settings[guild_id].add(channel_name)
        else:
            self.server_settings[guild_id].remove(channel_name)
        
        #Write the changes to file
        utils.write_channel_data("servers.dat", self.server_settings)
    
    def can_user_set(self, user, channel):
        """
        Currently uses whether a user can manage channels for if the user can use the commands.
        """
        perms = channel.permissions_for(user)
        return user.manage_channels or user.administrator
