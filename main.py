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
import mathParser
import polling
from typing import List, Dict
import os
import glob
import sys
import asyncio
import random

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

@bot.command(brief="View rules.",
             help="This command fetches the rules as they are defined in the rule-channel.",
             aliases=["regeln"])
async def rules(ctx):
    ruleChannel = bot.get_channel(bot_data.IDs['rule_channel'])
    ruleMsg = await ruleChannel.fetch_message(bot_data.IDs['rule_message'])
    await ctx.send(ruleMsg.content)

@bot.command(brief="Calculate constant math expressions.",
             help="This command tries to calculate constant mathematical expressions.\nNo variables allowed.\n\
                  \nValid constants and functions:\n - e, pi\n - sin, cos, tan, exp, sqrt, abs, trunc, round, sgn",
             usage="<expression>")
async def calc(ctx, *, arg):
    nsp = mathParser.NumericStringParser()
    try:
        result = nsp.eval(arg)
    except:
        result = f"Invalid expression. Type `{bot_data.prefix}help calc` for information on the command."
        print(f'Invalid \'calc\' expression: {arg}')
    await ctx.send(result)

@bot.command(brief="Generate random number",
             help="Generate a random number or randomly choose from multiple elements after the following pattern:\n\
                  \nrandom\t\t-> [0,1]\nrandom a\t-> [0,a]\nrandom a b\t-> [a,b]\nrandom a b c\t-> a or b or c or ...",
             aliases=['random'])
async def rand(ctx, *args):
    # /random       -> [0,1]
    # /random a     -> [0,a]
    # /random a b   -> [a,b]
    # /random a b c -> a or b or c or ...
    if not args:
        answer = str(random.random())
    elif len(args) == 1 and args[0].isdigit():
        answer = str(random.uniform(0.0, float(args[0])))
    elif len(args) == 2 and args[0].isdigit() and args[1].isdigit():
        answer = str(random.uniform(float(args[0]), float(args[1])))
    elif len(args) > 1:
        answer = str(random.choice(args))
    else:
        answer = 'Error: Invalid argument.'
    await ctx.send(answer)

bot.run(bot_data.token)
