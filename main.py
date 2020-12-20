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
import bot_database as db
import bot_help
from typing import List, Dict
import polling
import os
import glob
import sys
import asyncio

bot_data = db.bot_database()
bot = commands.Bot(command_prefix = bot_data.prefix)
# bot.help_command = bot_help.bot_helper()

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

@bot.event
async def on_message(message):
    """
    If possible don't define commands here. Use the command framework for that (see below)
    Only use this function if you are processing messages without commands.
    """

    # Code goes here

    await bot.process_commands(message)

# Commands go here =====================================================================================================
@bot.command(brief="Just for testing random stuff.",
             help="This function is for testing code. Don't expect any predictable behaviour from it.",
             aliases=["hilfe"])
async def test(ctx):
    await ctx.send('test received')
    pass

@bot.command(brief="Countdown from value. Default is 10s.",
             help="Start a countdown from a designated value or 10 seconds if none has been specified.",
             usage="<seconds>")
async def countdown(ctx, arg = "10"):
    if not arg.isdigit():
        counter = 10
    else:
        counter = int(arg)
    if counter > 500:
        await ctx.send('Dude, I don\'t have all day!')
        return
    msg = await ctx.send(f'Countdown: {counter}')
    while counter > 0:
        counter -= 1
        await asyncio.sleep(1)
        await msg.edit(content=(f'Countdown: {counter}' if counter != 0 else 'Countdown: **NOW**'))


bot.run(bot_data.token)