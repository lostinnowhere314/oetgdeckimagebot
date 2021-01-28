# oetgdeckimagebot
Discord bot for posting oEtG deck images.

To use:
1. In 'settings.dat', replace the text after DISCORD_TOKEN=... with your bot discord token (refer to https://discordpy.readthedocs.io/en/latest/discord.html) (Please do not push this and replace the template settings file)
2. Install the 'cairosvg' python package (unless you already have it); use 'pip install cairosvg' or equivalent
3. Run bot_start.py with python
Then, it should be running!

Once on the server that the bot is on, you can set it to post in a channel by typing '!deck enable' in that channel. Note that one needs the permission to manage channels to do this (intended to prevent random people from messing with it). Use '!deck help' to see the other few available commands.
