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
import os
import glob


# Modify class:
class bot_client(discord.Client):
    def startup(self):
        # Run this function once when the bot starts for the first time
        self.get_config()
        self.loadAllPolls()

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

    def loadAllPolls(self):
        if not os.path.exists('polls'):
            os.makedirs('polls')
            print('Created polls/ directory.')
            return
        pollFiles = glob.glob('polls/poll*.txt')
        for file in pollFiles:
            pollObj = polling.poll("dummy", [])
            pollObj.loadPoll(file)
            pollObj.id = self.nextPollID
            self.polls.append(pollObj)
            self.updatePoll(pollObj.id)

    def savePoll(self,poll: polling.poll, cleanup = True):
        poll.savePoll("polls/poll{0}.txt".format(poll.id))
        if cleanup:
            self.cleanupPollFiles()

    def cleanupPollFiles(self):
        # Compares IDs of polls on disk with those in memory
        # and deletes the ones that are not in memory from disk
        diskFiles = glob.glob('polls/poll*.txt')
        diskIDs = [int(filter(str.isdigit(), str(x))) for x in diskFiles]
        for diskID in diskIDs:
            existsInMemory = False
            for memPoll in self.polls:
                if memPoll.id == diskID:
                    existsInMemory = True
            if not existsInMemory:
                os.remove('polls/poll{0}.txt'.format(diskID))

    async def updatePoll(self,pollID: int):
        for poll in self.polls:
            if poll.id == pollID:
                channel = client.get_channel(poll.msgChannelID)
                message = await channel.fetch_message(poll.msgMessageID)
                await message.edit(content=poll.getPollMsg(self.prefix))
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
                dcMessage = await message.channel.send(newPoll.getPollMsg(client.prefix))
                newPoll.msgMessageID = dcMessage.id

                client.polls = client.polls + [newPoll]
                client.savePoll(newPoll)
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
                        client.savePoll(poll)
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
                        client.savePoll(poll)
                        return
            return

        # WICHTELN
        if misc.startswithElement(uCmd, ['wichtel']):
            # /wichteln "Anschrift_Name; MeineStraße 1a; 12345 MeinOrt; weiteres"
            await message.delete(delay=10.0)
            receiverStrs = re.findall('\".+?\"', message.clean_content)
            if len(receiverStrs) != 1:
                await message.channel.send("Error: Invalid syntax!", delete_after=5.0)
                return
            file = configparser.ConfigParser()
            file.read('wichteln.txt')
            if not file.has_section('PARTICIPANTS'):
                file.add_section('PARTICIPANTS')
            file['PARTICIPANTS'][str(message.author.id)] = receiverStrs[0]

            with open('wichteln.txt', 'w') as configfile:
                file.write(configfile)

            await message.channel.send('Du bist hiermit beim Wichteln dabei. Falls du deine Anschrift ändern willst, gib den command einfach nochmal ein.', delete_after=10.0)
            return

        # GIVE OUT WICHTELN ADDRESSES
        if uCmd.startswith('triggerwichteln'):
            file = configparser.ConfigParser()
            file.read('wichteln.txt')
            userIDs = []
            userDataRaw = []
            for section in file.sections():
                for (key, val) in file.items(section):
                    userIDs.append(key)
                    userDataRaw.append(val)
            # Shuffle userData to randomly assign addresses to users
            userData = misc.unique_shuffle_list(userDataRaw)
            for i in range(len(userIDs)):
                msg = "**Glückwunsch!\nZum Wichteln wurde dir die Person mit folgender Addresse zugeteilt:**\n{0}"\
                    .format(userData[i])
                user = client.get_user(int(userIDs[i]))
                await user.send(msg)
                print('Sent wichteln msg to {0}'.format(user.name))
            wChannel = client.get_channel(786935616465797121)
            await wChannel.send('Die Addressen wurden soeben unter den Teilnehmern aufgeteilt. Falls sich jemand mit `/wichteln "..."` eingetragen hat, aber keine Privatnachricht bekommen hat, bitte an DaMoIsHere wenden!')

            if not file.has_section('ZUTEILUNG'):
                file.add_section('ZUTEILUNG')
            for i in range(len(userIDs)):
                file['ZUTEILUNG'][str(userIDs[i])] = userData[i]

            with open('wichteln.txt', 'w') as configfile:
                file.write(configfile)
            return


        # Eastereggs
        if misc.startswithElement(uCmd, ['music', 'play', 'skip', 'queue']):
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
