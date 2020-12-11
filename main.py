'''
If you don't know what the fuck is going on here then I humbly suggest you read the documentation:
https://discordpy.readthedocs.io/en/latest/index.html#

'''

import discord
import configparser
import mathParser
import misc_functions as misc
import polling
import re  # regex
import random


# Modify class:
class bot_client(discord.Client):
    def startup(self):
        # Run this function once when the bot starts for the first time
        self.get_config()

    def get_config(self):
        configFile = configparser.ConfigParser()
        configFile.read('config.txt')
        self.token = configFile['BASE']['token']
        self.prefix = configFile['BASE']['prefix']
        self.panic_msg = configFile['BASE']['panic_msg']
        self.ruleChannelID = int(configFile['RULES']['channelID'])
        self.ruleMessageID = int(configFile['RULES']['messageID'])
        self.quoteChannelID = int(configFile['QUOTES']['channelID'])
        self.activityName = configFile['ACTIVITY']['name']

    async def updatePoll(self,pollID: int):
        for poll in self.polls:
            if poll.id == pollID:
                channel = client.get_channel(poll.msgChannelID)
                message = await channel.fetch_message(poll.msgMessageID)
                await message.edit(content = poll.getPollMsg())
                return

    # Parameters:
    token = ''
    prefix = ''
    panic_msg = ''
    ruleChannelID = -1
    ruleMessageID = -1
    quoteChannelID = -1
    activityName = ''

    # Variables
    mood = 'neutral'
    polls = []
    nextPollID = 0

# Callbacks:
client = bot_client()


@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    game = discord.Game(client.activityName)
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
    # Bot doesn't answer itself:
    if message.author == client.user:
        return

    # === INTERPRET CHAT ===

    nice = re.search('[^\d]69[^\d]*|[^\d]*69[^\d]', message.clean_content)
    if nice:
        await message.channel.send("Nice!")
        return

    # look for commands:
    if message.content.startswith(client.prefix):
        # Remove prefix and make lowercase:
        uCmd = message.content[len(client.prefix):].lower()

        # HELP
        # before: if uCmd.startswith("help"):
        if misc.startswithElement(uCmd, ["help", "hilfe"]):
            await message.channel.send(misc.get_help_msg(client.prefix))
            return

        # RULES
        if misc.startswithElement(uCmd, ["rules", "regel"]):
            ruleChannel = client.get_channel(client.ruleChannelID)
            ruleMsg = await ruleChannel.fetch_message(client.ruleMessageID)
            await message.channel.send(ruleMsg.content)
            return

        # CALC
        if uCmd.startswith("calc"):
            expression = message.content[len(client.prefix + "calc"):]
            nsp = mathParser.NumericStringParser()
            try:
                result = nsp.eval(expression)
            except:
                result = client.panic_msg
                print("Invalid command: {0}".format(message.content))

            await message.channel.send(result)
            return

        # RANDOM
        if misc.startswithElement(uCmd, ["random"]):
            # Valid cases:
            # 1. /random               -> [0,1]
            # 2. /random a b           -> [a,b]
            # 3. /random a b c d ...   -> a or b or c or d or ...

            # Turn all ',' into '.':
            uCmd = re.sub(',', '.', uCmd)
            # Find all numbers in command:
            nums = re.findall("\d+\.?\d*", uCmd)

            # Convert to floats:
            flnums = [float(z) for z in nums]

            try:
                if len(flnums) == 0:
                    # CASE 1
                    answer = str(random.random())
                elif len(flnums) == 2:
                    # CASE 2
                    if flnums[0].is_integer() and flnums[1].is_integer():
                        # If they are ints
                        answer = str(random.randrange(int(flnums[0]), int(flnums[1])))
                    else:
                        # If they are floats
                        answer = str(random.uniform(flnums[0], flnums[1]))
                elif len(flnums) > 2:
                    # CASE 3
                    answer = str(random.choice(nums))
                else:
                    answer = client.panic_msg
            except:
                answer = client.panic_msg
            await message.channel.send(answer)
            return

        # QUOTES
        if misc.startswithElement(uCmd, ["quote", "zitat"]):
            quote = re.findall('".+?"', message.clean_content)
            # Check valid syntax:
            if len(quote) < 2 or len(quote) > 3:
                await message.channel.send(client.panic_msg)
                return

            prof_name: str = quote[0].lower().strip('"')
            prof_quote: str = quote[1]
            if len(quote) == 3:
                prof_context: str = quote[2]
            else:
                prof_context: str = '"No Context given"'

            # Read quote count for that prof:
            ifile = configparser.ConfigParser()
            ifile.read("quotes.txt")
            try:
                quote_count: int = int(ifile[prof_name]['count'])
            except:
                quote_count: int = 0

            try:
                ofile = configparser.ConfigParser()
                ofile.read('quotes.txt')
                if not ofile.has_section(prof_name):
                    ofile.add_section(prof_name)
                ofile.set(prof_name, 'count', str(quote_count + 1))
                ofile.set(prof_name, 'q#' + str(quote_count), prof_quote + " " + prof_context)

                with open('quotes.txt', 'w') as configfile:
                    ofile.write(configfile)
                await message.channel.send("Saved quote.")
            except:
                await message.channel.send(client.panic_msg)
                print("Error handling quote: {0}".format(message.content))
                return
            # Send to quote Channel:
            if client.quoteChannelID != -1:
                msg = ":\n**Person:** {0}\n**Zitat:** {1}\n**Kontext:** {2}".format(prof_name, prof_quote, prof_context)
                channel = client.get_channel(client.quoteChannelID)
                await channel.send(msg)
            return

        # POLLING
        if misc.startswithElement(uCmd, ['poll', 'vote', 'unvote']):
            # Delete Message for anonymity:
            await message.delete()
            if uCmd.startswith('poll'):
                args = re.findall('".+?"', message.clean_content)
                if len(args) <= 1:
                    await message.channel.send("Error: Not enough arguments!", delete_after=5.0)
                    print("Invalid poll syntax: {0}".format(message.clean_content[(len(client.prefix)+4):]))
                    return
                newPoll = polling.poll(args[0].strip('"'), [z.strip('"') for z in args[1:]])
                newPoll.authorID = message.author.id
                newPoll.authorName = message.author.name
                newPoll.msgChannelID = message.channel.id
                newPoll.id = client.nextPollID
                client.nextPollID += 1
                dcMessage = await message.channel.send(newPoll.getPollMsg())
                newPoll.msgMessageID = dcMessage.id

                client.polls = client.polls + [newPoll]
            elif uCmd.startswith('vote'):
                # /vote <pollID> <optID>

                args = re.findall('\d+', message.clean_content)
                if len(args) != 2:
                    await message.channel.send("Error: Invalid number of arguments!", delete_after=5.0)
                    print("Invalid vote syntax: {0}".format(message.clean_content[(len(client.prefix)+4):]))
                    return
                pollID = int(args[0])
                optID = int(args[1])
                for poll in client.polls:
                    if poll.id == pollID:
                        poll.voteOption(optID, message.author.id)
                        await client.updatePoll(pollID)
                        return
            elif uCmd.startswith('unvote'):
                # /vote <pollID> <optID>

                args = re.findall('\d+', message.clean_content)
                if len(args) != 2:
                    await message.channel.send('Error: Invalid number of arguments!', delete_after=5.0)
                    print("Invalid unvote syntax: {0}".format(message.clean_content[(len(client.prefix)+4):]))
                    return
                pollID = int(args[0])
                optID = int(args[1])
                for poll in client.polls:
                    if poll.id == pollID:
                        poll.unvoteOption(optID, message.author.id)
                        await client.updatePoll(pollID)
                        return
            return

        # Eastereggs

        if uCmd == "music" or message.content.startswith(client.prefix + "play") \
                or message.content.startswith(client.prefix + "skip") \
                or message.content.startswith(client.prefix + "queue"):
            await message.channel.send("I'm not the droid you're looking for!")
            return

        if uCmd.startswith('cry'):
            client.mood = 'crying'
            await message.channel.send(" :sob: I'm crying now. You made me cry. Are you happy now? :sob:")
            return

        if uCmd == 'sorry' or uCmd == 'sry':
            if client.mood != 'neutral':
                client.mood = 'neutral'
                await message.channel.send('Fuck off! :unamused:')
            else:
                await message.channel.send('it\'s fine')
            return

        if uCmd == 'rage':
            client.mood = "angry"
            await message.channel.send('Grrrrrr :rage:')
            return

        if uCmd.startswith('captcha'):
            await message.channel.send('I\'m not a robot I swear!')
            return

        if uCmd.startswith('putin'):
            await message.channel.send('All hail Putin! \n\t\t\t⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣵⣿⣿⣿⠿⡟⣛⣧⣿⣯⣿⣝⡻⢿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⠋⠁⣴⣶⣿⣿⣿⣿⣿⣿⣿⣦⣍⢿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⢷⠄⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⢼⣿⣿⣿⣿\n\
            ⢹⣿⣿⢻⠎⠔⣛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣿⣿⣿⣿\n\
            ⢸⣿⣿⠇⡶⠄⣿⣿⠿⠟⡛⠛⠻⣿⡿⠿⠿⣿⣗⢣⣿⣿⣿⣿\n\
            ⠐⣿⣿⡿⣷⣾⣿⣿⣿⣾⣶⣶⣶⣿⣁⣔⣤⣀⣼⢲⣿⣿⣿⣿\n\
            ⠄⣿⣿⣿⣿⣾⣟⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⢟⣾⣿⣿⣿⣿\n\
            ⠄⣟⣿⣿⣿⡷⣿⣿⣿⣿⣿⣮⣽⠛⢻⣽⣿⡇⣾⣿⣿⣿⣿⣿\n\
            ⠄⢻⣿⣿⣿⡷⠻⢻⡻⣯⣝⢿⣟⣛⣛⣛⠝⢻⣿⣿⣿⣿⣿⣿\n\
            ⠄⠸⣿⣿⡟⣹⣦⠄⠋⠻⢿⣶⣶⣶⡾⠃⡂⢾⣿⣿⣿⣿⣿⣿\n\
            ⠄⠄⠟⠋⠄⢻⣿⣧⣲⡀⡀⠄⠉⠱⣠⣾⡇⠄⠉⠛⢿⣿⣿⣿\n\
            ⠄⠄⠄⠄⠄⠈⣿⣿⣿⣷⣿⣿⢾⣾⣿⣿⣇⠄⠄⠄⠄⠄⠉⠉\n\
            ⠄⠄⠄⠄⠄⠄⠸⣿⣿⠟⠃⠄⠄⢈⣻⣿⣿⠄⠄⠄⠄⠄⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⢿⣿⣾⣷⡄⠄⢾⣿⣿⣿⡄⠄⠄⠄⠄⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠸⣿⣿⣿⠃⠄⠈⢿⣿⣿⠄⠄⠄⠄⠄⠄⠄')
            return

        if misc.startswithElement(uCmd, ['trump', 'donald', 'orangeman']):
            await message.channel.send('STOP THE COUNT! \n\t\t\t⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠋⠉⡉⣉⡛⣛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠄⠄⠄⠄⠄⢀⣸⣿⣿⡿⠿⡯⢙⠿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡿⠄⠄⠄⠄⠄⡀⡀⠄⢀⣀⣉⣉⣉⠁⠐⣶⣶⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠁⣿⣿⣀⠈⠿⢟⡛⠛⣿⠛⠛⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡆⠄⠄⠄⠄⠄⠈⠁⠰⣄⣴⡬⢵⣴⣿⣤⣽⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡇⠄⢀⢄⡀⠄⠄⠄⠄⡉⠻⣿⡿⠁⠘⠛⡿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⡿⠃⠄⠄⠈⠻⠄⠄⠄⠄⢘⣧⣀⠾⠿⠶⠦⢳⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣶⣤⡀⢀⡀⠄⠄⠄⠄⠄⠄⠻⢣⣶⡒⠶⢤⢾⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⡿⠟⠋⠄⢘⣿⣦⡀⠄⠄⠄⠄⠄⠉⠛⠻⠻⠺⣼⣿⠟⠋⠛⠿⣿⣿\n\
            ⠋⠉⠁⠄⠄⠄⠄⠄⠄⢻⣿⣿⣶⣄⡀⠄⠄⠄⠄⢀⣤⣾⣿⣿⡀⠄⠄⠄⠄⢹\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢻⣿⣿⣿⣷⡤⠄⠰⡆⠄⠄⠈⠉⠛⠿⢦⣀⡀⡀⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⢿⣿⠟⡋⠄⠄⠄⢣⠄⠄⠄⠄⠄⠄⠄⠈⠹⣿⣀\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠘⣷⣿⣿⣷⠄⠄⢺⣇⠄⠄⠄⠄⠄⠄⠄⠄⠸⣿\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠹⣿⣿⡇⠄⠄⠸⣿⡄⠄⠈⠁⠄⠄⠄⠄⠄⣿\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢻⣿⡇⠄⠄⠄⢹⣧⠄⠄⠄⠄⠄⠄⠄⠄⠘')
            return

        if uCmd.startswith('reverse') or uCmd.startswith('undo') or uCmd.startswith('Konter'):
            await message.channel.send("take that! \n\t\t\t⠐⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠂\n\
            ⠄⠄⣰⣾⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⠄⠄\n\
            ⠄⠄⣿⣿⣿⡿⠋⠄⡀⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠋⣉⣉⣉⡉⠙⠻⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣇⠔⠈⣿⣿⣿⣿⣿⡿⠛⢉⣤⣶⣾⣿⣿⣿⣿⣿⣿⣦⡀⠹⠄⠄\n\
            ⠄⠄⣿⣿⠃⠄⢠⣾⣿⣿⣿⠟⢁⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⡟⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⠋⢠⣾⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⡿⠁⣰⣿⣿⣿⣿⣿⣿⣿⣿⠗⠄⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⡟⠄⠄\n\
            ⠄⠄⣿⡿⠁⣼⣿⣿⣿⣿⣿⣿⡿⠋⠄⠄⠄⣠⣄⢰⣿⣿⣿⣿⣿⣿⣿⠃⠄⠄\n\
            ⠄⠄⡿⠁⣼⣿⣿⣿⣿⣿⣿⣿⡇⠄⢀⡴⠚⢿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢠⠄⠄\n\
            ⠄⠄⠃⢰⣿⣿⣿⣿⣿⣿⡿⣿⣿⠴⠋⠄⠄⢸⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾⠄⠄\n\
            ⠄⠄⢀⣿⣿⣿⣿⣿⣿⣿⠃⠈⠁⠄⠄⢀⣴⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾⣿⠄⠄\n\
            ⠄⠄⢸⣿⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⢶⣿⣿⣿⣿⣿⣿⣿⣿⠏⢀⣾⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⠋⣠⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣼⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢁⣴⣿⣿⣿⣿⠗⠄⠄⣿⣿⠄⠄\n\
            ⠄⠄⣆⠈⠻⢿⣿⣿⣿⣿⣿⣿⠿⠛⣉⣤⣾⣿⣿⣿⣿⣿⣇⠠⠺⣷⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣦⣄⣈⣉⣉⣉⣡⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⠉⠁⣀⣼⣿⣿⣿⠄⠄\n\
            ⠄⠄⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣾⣿⣿⡿⠟⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄")
            return

        # This line is only reached if no command has been recognized. Act accordingly:
        await message.channel.send('I am afraid I can\'t do that {0.author.name}.'.format(message))
        print("Unrecognized command: {0}".format(message.content))


client.startup()
client.run(client.token)
