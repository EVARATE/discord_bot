"""
This is a complete rewrite of the discord bot. Before every message was scanned for commands with
if/else statements which is kindof messy.
The goal of this rewrite is to use the existing command framework of the discord.py library.

Here is its documentation:
https://discordpy.readthedocs.io/en/latest/index.html
"""

# imports
import discord
from discord.ext import tasks, commands
import configparser
import bot_database as db
import mathParser
import polling
import tictactoe
import connect_four
import party_notifier
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
    # Only add cogs on first init:
    bot.add_cog(polling.Poll_Commands(bot, bot_data))
    bot.add_cog(tictactoe.tic_tac_toe(bot))
    bot.add_cog(party_notifier.Party_Notifier(bot, bot_data))
    # bot.add_cog(connect_four.connect_four(bot))


    # Set activity:
    if bot_data.activity_name != '-1':
        game = discord.Game(bot_data.activity_name)
        await bot.change_presence(status=discord.Status.online, activity=game)
    else:
        await bot.change_presence(status=None, activity=None)

    print(f'Bot logged in as {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    # This function looks if any channel has more than a set number of participants
    # and if it does, sends a notification

    notif_channel = bot.get_channel(bot_data.IDs['notification_channel'])

    with open(bot_data.datapath + 'party_channels.txt', 'r') as file:
        partyChannelIDs = [int(x[:-1]) for x in file.readlines()]

    # CHECKS
    # If channel has become empty, unmark it as party channel
    if before.channel is not None and len(before.channel.members) == 0:
        if before.channel.id in bot_data.party_channels:
            bot_data.party_channels = bot_data.party_channels - {int(before.channel.id)}
            await notif_channel.send(f'The party in **{before.channel.name}** has ended.')
        return

    if after.channel is None:
        return

    if after.channel.id not in partyChannelIDs:
        return

    # See if channel is already a party channel
    if after.channel.id in bot_data.party_channels:
        return
    else:
        bot_data.party_channels = bot_data.party_channels.union({int(after.channel.id)})

    print(bot_data.party_channels)

    if len(after.channel.members) >= bot_data.party_count:
        # Do this weird thing to get the guild and its roles
        this_guild = after.channel.guild
        party_role = this_guild.get_role(bot_data.IDs['party_role'])

        await notif_channel.send(f'{party_role.mention} There seems to be a party in **{after.channel.name}**')
        return


@bot.event
async def on_message(message):
    """
    If possible don't define commands here. Use the command framework for that (see below)
    Only use this function if you are processing messages without commands.
    """

    # Code goes here

    if message.author == bot.user:
        return
    """ 
    Random Estereggs
    """


    if ('Mo ' or 'Mo,' or 'Mo.' or 'Mo!' or 'Mo?') in message.content or message.content == 'Mo':
        await message.channel.send('Habe ich etwas von meinem Meister, Herrn und Gebieter Mo gehört? :heart_eyes:', delete_after= 20)

    if message.content == "Hello there!":
        await message.channel.send("General Kenobi! You are a bold one! Hehehehe KILL HIM!")
        await message.channel.send("https://gph.is/2pE8sbx")
        return

    if 'scrinzi' in message.content.lower():
        await message.channel.send('Scrinzi, so ein Sack! :face_vomiting:', delete_after=5)
        return

    await bot.process_commands(message)

class Main_Commands(commands.Cog):
    """
    This cog contains all the main commands which don't really fit into another cog.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Just for testing random stuff.",
                 help="This function is for testing code. Don't expect any predictable behaviour from it.")
    async def test(self, ctx):
        pass

    @commands.command(brief="Countdown from value. Default is 10s.",
                 help="Start a countdown from a designated value or 10 seconds if none has been specified.",
                 usage="<seconds>")
    async def countdown(self, ctx, arg = "10"):
        if not arg.isdigit():
            counter = 10
        else:
            counter = int(arg)
        if counter > 500:
            await ctx.send('Dude, I don\'t have all day!', delete_after=10.0)
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
                      \nValid constants and functions:\n - e, pi, c, h, k\n - sin, sinh, asin, asinh, cos, cosh, acos, acosh, tan, atan, atan2, atanh, exp, expm1, ln, lg, sqrt, abs, trunc, round, sgn",
                 usage="<expression>")
    async def calc(self, ctx, *, arg):
        nsp = mathParser.NumericStringParser()
        try:
            result = nsp.eval(arg)
        except:
            await ctx.send(f"Invalid expression. Type `{bot_data.prefix}help calc` for information on the command.",
                           delete_after=10.0)
            print(f'Invalid \'calc\' expression: {arg}')
            return
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
        await ctx.message.delete()
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
            await ctx.send('Saved quote.', delete_after=10)
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

    @commands.check(is_admin)
    @commands.command(brief="Lock access to the 'echo' command.",
                      help="With this command you can lock the 'echo' command.\
                           \n\necholock\t-> Show current lock status\necholock toggle\t-> Toggle lock\
                            \n\nAlternatives to 'toggle' are 'switch' and 'change'",
                      usage="[<none>, toggle, switch, change]")
    async def echolock(self, ctx, *args):
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
            await self.bot.change_presence(status=discord.Status.online, activity=game)
            configStr: str = arg

        # Save to config
        config = configparser.ConfigParser()
        config.read('config.txt')
        config.set('BASE', 'activity_name', configStr)

        with open('config.txt', 'w') as configfile:
            config.write(configfile)

    @commands.command(brief="Convert weight to usable units.",
                      help='This command converts your mass (kg) to its corresponding resting energy in '
                           'kilotons of TNT. This is equivalent to half the energy released in the explosion of you'
                           ' touching your anti-matter twin.\nThis is also a great way of calling random people fat.',
                      usage='<mass in kg>')
    async def weight(self, ctx, *, arg):
        # Make lowercase in case someone entered units:
        arg = arg.lower()

        # Scan for cancer:
        if misc.element_in_str(['grain', 'gr', 'drachm', 'dr', 'ounce', 'oz', 'pound', 'lb', 'stone', 'st',
                                'quarter', 'qr', 'qtr', 'hundretweight', 'cwt', 'slug'], arg):
            admin_role = ctx.guild.get_role(bot_data.IDs['admin_role'])
            await ctx.send(f"{admin_role.mention} **IMPERIAL UNITS DETECTED!!!** Authorities were notified. Stay where you are criminal scum!")
            return


        # Detect units:
        factor = 1.0
        if arg.endswith('kg'):
            arg = arg[0:-2]
        elif arg.endswith('g'):
            arg = arg[0:-1]
            factor = 1. / 1000.0
        elif arg.endswith('t'):
            arg = arg[0:-1]
            factor = 1000
        elif arg.endswith('u'):
            arg = arg[0:-1]
            factor = 6.0221e26
        elif arg.endswith('tev/c^2'):
            arg = arg[0:-7]
            factor = 5.60852495e23
        elif arg.endswith('tev/c²'):
            arg = arg[0:-6]
            factor = 5.60852495e23
        elif arg.endswith('gev/c^2'):
            arg = arg[0:-7]
            factor = 5.60852495e26
        elif arg.endswith('gev/c²'):
            arg = arg[0:-6]
            factor = 5.60852495e26
        elif arg.endswith('kev/c^2'):
            arg = arg[0:-7]
            factor = 5.60852495e29
        elif arg.endswith('kev/c²'):
            arg = arg[0:-6]
            factor = 5.60852495e29
        elif arg.endswith('ev/c^2'):
            arg = arg[0:-6]
            factor = 5.60852495e32
        elif arg.endswith('ev/c²'):
            arg = arg[0:-5]
            factor = 5.60852495e32
        else:
            factor = 1.0

        # If arg still has non-digit chars, it is an error
        if not arg.isdigit():
            # Detect mathematical expressions:
            nsp = mathParser.NumericStringParser()
            try:
                arg = nsp.eval(arg)
            except:
                await ctx.send('Error: Could not parse argument. Use something like `10 kg` or just `10`.', delete_after=10)
                return

        E = float(arg) * factor * (2.998e8)**2
        Joule_to_gigatonTNT = 2.390e-19
        hiroshima_energy = 16e-6   # gigatons of TNT

        GT_mass_raw = E * Joule_to_gigatonTNT
        if GT_mass_raw >= 1e3:
            explosion_str = f'{round(GT_mass_raw * 1e-3, 2)} terratons'
        elif GT_mass_raw < 1e3 and GT_mass_raw >= 1:
            explosion_str = f'{round(GT_mass_raw, 2)} gigatons'
        elif GT_mass_raw < 1 and GT_mass_raw >= 0.001:
            explosion_str = f'{round(GT_mass_raw * 1e3, 2)} megatons'
        elif GT_mass_raw < 1e-3 and GT_mass_raw >= 1e-6:
            explosion_str = f'{round(GT_mass_raw * 1e6, 2)} kilotons'
        else:
            explosion_str = f'{round(GT_mass_raw * 1e9, 2)} tons'

        # Hiroshima formatting:
        hir_fac = round(GT_mass_raw / hiroshima_energy, 1)
        hir_str = f'or **{hir_fac}** hiroshima bombs**' if hir_fac >= 1 else ''

        # For the lulz:
        if float(arg) * factor >= 100:
            pref = '**WOW!** '
            suff = 'Damn.'
        else:
            pref = ''
            suff = ''

        text = f'{pref}This mass is equivalent to a very generous **{explosion_str} of TNT** {hir_str}. {suff}'
        await ctx.send(text)

    @commands.command(brief="cry",
                      help=" show the only emotion HAL is currently capable of")
    async def cry(self, ctx):
        await ctx.send(':sob:')
        await asyncio.sleep(5)
        await ctx.send('http://gph.is/2f4QMDC', delete_after = 10)

    @commands.command(brief = 'let HAL show you his Magic')
    async def draw_card(self, ctx):
        await ctx.send('Your Card is the Ace of Spades', delete_after = 40)
        await asyncio.sleep(7)
        await ctx.send('shuffeling the deck',delete_after = 10)
        await asyncio.sleep(3)
        await ctx.send('trust me bro', delete_after = 3)
        await asyncio.sleep(7)
        await ctx.send('Was this your card:', delete_after = 23)
        await asyncio.sleep(3)
        await ctx.send('http://gph.is/1UPsMwn', delete_after = 20)
        await ctx.send('The ACE OF SPADES!')
        await asyncio.sleep(5)
        await ctx.send('not impressed?', delete_after = 5)
        await asyncio.sleep(5)
        await ctx.send('https://gph.is/g/aNMKlwP', delete_after = 10)
        await ctx.send('http://gph.is/1oKXMOp', delete_after = 10)



bot.add_cog(Main_Commands(bot))
bot.run(bot_data.token)
