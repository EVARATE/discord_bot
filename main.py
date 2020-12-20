"""
This is a complete rewrite of the discord bot. Before every message was scanned for commands with
if/else statements which is kindof messy.
The goal of this rewrite is to use the existing command framework of the discord.py library.

Here is its documentation:
https://discordpy.readthedocs.io/en/latest/index.html
"""

# imports
import discord
from discord.ext import commands
import configparser
from typing import List, Dict
import polling
import os
import glob
import sys


class bot_database():
    """
    This class has nothing to do with the bot directly. It just stores all kinds of variables and other data
    the bot needs.
    """
    token: str = ''
    prefix: str = ''
    IDs: Dict[str, int] = {}

    def __init__(self,filepath: str = ''):
        # Initialize empty arrays:
        self.IDs = {}

        # 'config.txt' must be in local directory, create it if not
        if not os.path.exists('config.txt'):
            # Create template file:
            config = configparser.ConfigParser()
            config.add_section('BASE')
            config.add_section('IDs')

            config.set('BASE', 'token', '-1')
            config.set('BASE', 'prefix', '/')

            config.set('IDs', 'admin_role', '-1')
            config.set('IDs', 'rule_channel', '-1')
            config.set('IDs', 'rule_message', '-1')
            config.set('IDs', 'quote_channel', '-1')

            with open('config.txt', 'w') as configfile:
                config.write(configfile)

            print('Created \'config.txt\'. Please enter available values and restart.')
            sys.exit()
        else:
            # Try to read 'config.txt':
            try:
                config = configparser.ConfigParser()
                config.read('config.txt')
                self.token = config['BASE']['token']
                self.prefix = config['BASE']['prefix']

                for (ID_key, val) in config.items('IDs'):
                    self.IDs[ID_key] = val

            except:
                print('Error reading \'config.txt\'. Please fix it or delete it to generate a new one. Aborting.')
                sys.exit()

        print('Successfully loaded database.')




bot_data = bot_database()
bot = commands.Bot(command_prefix = bot_data.prefix)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

# Commands go here
@bot.command()
async def test(ctx):
    await ctx.send('test received')
    pass

bot.run(bot_data.token)