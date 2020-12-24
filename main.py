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
import mathParser
import polling
import misc_functions as misc
from typing import List, Dict
import os
import glob
import sys
import asyncio
import random

bot_data = db.bot_database()
bot = commands.Bot(command_prefix = bot_data.prefix)

# CHECKS

def is_admin(ctx):
    admin_role = ctx.guild.get_role(bot_data.IDs['admin_role'])
    return admin_role in ctx.author.roles


@bot.event
async def on_ready():
    bot.add_cog(polling.Poll_Commands(bot, bot_data))
    print(f'Bot logged in as {bot.user}')

    # Set activity:
    if bot_data.activity_name != '-1':
        game = discord.Game(bot_data.activity_name)
        await bot.change_presence(status=discord.Status.idle, activity=game)
    else:
        await bot.change_presence(status=None, activity=None)

@bot.event
async def on_message(message):
    """
    If possible don't define commands here. Use the command framework for that (see below)
    Only use this function if you are processing messages without commands.
    """

    # Code goes here

    await bot.process_commands(message)


class Main_Commands(commands.Cog):
    """
    This cog contains all the main commands which don't really fit into another cog.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Just for testing random stuff.",
                 help="This function is for testing code. Don't expect any predictable behaviour from it.",
                 aliases=["hilfe"])
    async def test(self, ctx):
        await ctx.send(f'Prefix in db is {bot_data.prefix}')

    @commands.command(brief="Countdown from value. Default is 10s.",
                 help="Start a countdown from a designated value or 10 seconds if none has been specified.",
                 usage="<seconds>")
    async def countdown(self, ctx, arg = "10"):
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

    @commands.command(brief="View rules.",
                 help="This command fetches the rules as they are defined in the rule-channel.",
                 aliases=["regeln"])
    async def rules(self, ctx):
        ruleChannel = bot.get_channel(bot_data.IDs['rule_channel'])
        ruleMsg = await ruleChannel.fetch_message(bot_data.IDs['rule_message'])
        await ctx.send(ruleMsg.content)

    @commands.command(brief="Calculate constant math expressions.",
                 help="This command tries to calculate constant mathematical expressions.\nNo variables allowed.\n\
                      \nValid constants and functions:\n - e, pi\n - sin, cos, tan, exp, sqrt, abs, trunc, round, sgn",
                 usage="<expression>")
    async def calc(self, ctx, *, arg):
        nsp = mathParser.NumericStringParser()
        try:
            result = nsp.eval(arg)
        except:
            await ctx.send(f"Invalid expression. Type `{bot_data.prefix}help calc` for information on the command.",
                           delete_after=10.0)
            print(f'Invalid \'calc\' expression: {arg}')
        await ctx.send(result)

    @commands.command(brief="Generate random number",
                 help="Generate a random number or randomly choose from multiple elements after the following pattern:\n\
                      \nrandom\t\t-> [0,1]\nrandom a\t-> [0,a]\nrandom a b\t-> [a,b]\nrandom a b c\t-> a or b or c or ...",
                 aliases=['random'])
    async def rand(self, ctx, *args):
        if not args:
            answer = str(random.random())
        elif len(args) == 1 and args[0].isdigit():
            answer = str(random.uniform(0.0, float(args[0])))
        elif len(args) == 2 and args[0].isdigit() and args[1].isdigit():
            answer = str(random.uniform(float(args[0]), float(args[1])))
        elif len(args) > 1:
            answer = str(random.choice(args))
        else:
            await ctx.send(f'Error: Invalid argument. Type `{bot_data.prefix}help random` for information on the command.',
                           delete_after=10.0)
            return
        await ctx.send(answer)

    @commands.command(brief="Save Quote.",
                 help="Save a quote, its author and optionally information on the context of the quote.\
                      \nIf available the quote will also be sent to a dedicated text channel.",
                 usage='"<Author>" "<Quote>" "<Optional context>"')
    async def quote(self, ctx, *args):
        if len(args) < 2 or len(args) > 3:
            await ctx.send(f"Error: Invalid arguments. Type `{bot_data.prefix}help quote` for information on the command",
                           delete_after=10.0)
            return

        author_name: str = args[0].lower()
        quote_text: str = args[1]
        if len(args) == 3:
            quote_context = args[2]
        else:
            quote_context = "No Context given"

        qfile = configparser.ConfigParser()
        qfile.read(f'{bot_data.datapath}quotes.txt')
        try:
            quote_count: int = int(qfile[author_name]['count'])
        except:
            quote_count: int = 0

        try:
            if not qfile.has_section(author_name):
                qfile.add_section(author_name)
            qfile.set(author_name, 'count', str(quote_count + 1))
            qfile.set(author_name, f'q#{quote_count}', f'"{quote_text}" "{quote_context}"')

            with open(f'{bot_data.datapath}quotes.txt', 'w') as configfile:
                qfile.write(configfile)
            if bot_data.IDs['quote_channel'] != -1:
                quote_channel = bot.get_channel(bot_data.IDs['quote_channel'])
                await quote_channel.send(f':\n**Person:** {author_name}\
                                            \n**Zitat:** {quote_text}\
                                            \n**Kontext:** {quote_context}')
            await ctx.send('Saved quote.')
        except:
            await ctx.send(f'There was an error saving the quote. Type `{bot_data.prefix}help quote` for correct format.',
                           delete_after=10.0)

    @commands.command(brief="Make the bot say something.",
                      help="Let the bot say something. Your original message will be deleted. Mentions will be converted to text.",
                      usage="<text>")
    async def echo(self, ctx, *, arg):
        await ctx.message.delete()
        if bot_data.locks['echo'] or is_admin(ctx):
            await ctx.send(arg)
        else:
            await ctx.send('Error: This command is currently locked.', delete_after=10.0)

    @commands.command(brief="Lock access to the 'echo' command.",
                      help="With this command you can lock the 'echo' command.\
                           \n\necholock\t-> Show current lock status\necholock toggle\t-> Toggle lock\
                            \n\nAlternatives to 'toggle' are 'switch' and 'change'",
                      usage="[<none>, toggle, switch, change]")
    async def echolock(self, ctx, *args):
        if not is_admin(ctx):
            await ctx.send('Error: You do not have permission to run this command.', delete_after=10.0)
            return

        arg = args[0] if len(args) > 0 else ""
        if arg in ['toggle', 'switch', 'change']:
            bot_data.locks['echo'] = not bot_data.locks['echo']
            statusStr = "unlocked" if bot_data.locks['echo'] else "locked"

            # Update 'config.txt':
            config = configparser.ConfigParser()
            config.read('config.txt')
            config.set('LOCKS', 'echo', str(misc.bool_to_int(bot_data.locks['echo'])))

            with open('config.txt', 'w') as configfile:
                config.write(configfile)

            await ctx.send(f'`{bot_data.prefix}echo` is now **{statusStr}**')
        elif len(arg) == 0:
            statusStr = "unlocked" if bot_data.locks['echo'] else "locked"
            await ctx.send(f'`{bot_data.prefix}echo` is **{statusStr}**')
        else:
            await ctx.send(f'Error: Invalid argument. See `{bot_data.prefix}help echo` for information on the command.')

    @commands.check(is_admin)
    @commands.command(brief="Change the 'Playing' status of the bot.",
                      help = "Changes the 'Playing' status of the bot to the specified text. If no argument is given the status will be removed.")
    async def setactivity(self, ctx, *args):
        if not args:
            await self.bot.change_presence(status=None, activity=None)
            configStr: str = '-1'
        else:
            arg = ' '.join(args)
            game = discord.Game(arg)
            await self.bot.change_presence(status=discord.Status.idle, activity=game)
            configStr: str = arg

        # Save to config
        config = configparser.ConfigParser()
        config.read('config.txt')
        config.set('BASE', 'activity_name', configStr)

        with open('config.txt', 'w') as configfile:
            config.write(configfile)


bot.add_cog(Main_Commands(bot))
bot.run(bot_data.token)
