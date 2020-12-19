import configparser
import re
import misc_functions as misc
from typing import List


class pollOption:
    def __init__(self):
        self.voterIDs = []

    id: int = -1
    value: str = ''
    voterIDs: List[int] = []

    def hasVoted(self, voterID: str) -> bool:
        if voterID in self.voterIDs:
            return True
        return False


class poll:
    id: int = -1
    topic: str = ''
    options: List[pollOption] = []

    # Metadata:
    authorName: str = ''
    authorID: int = -1
    msgChannelID: int = -1
    msgMessageID: int = -1
    isClosed: bool = False
    custOpt: bool = False
    multiChoice: bool = False
    nextOptID: int = 1

    def __init__(self, question: str, options: list):
        # This is necessary to keep the lists contained to this instance of the class:
        self.options = []

        self.topic = question
        for opt in options:
            self.addOption(opt)

    def addOption(self, newOption: str):
        if len(newOption) != 0:
            opt = pollOption()
            opt.id = self.getOptID()
            opt.value = newOption
            self.options.append(opt)

    def addExOption(self, existingOption: pollOption):
        self.options.append(existingOption)

    def remOption(self, optionID: int):
        for opt in self.options:
            if opt.id == optionID:
                self.options.remove(opt)

    def voteOption(self, optionID: int, voterID: int):
        if not self.hasVoted(voterID):
            for opt in self.options:
                if opt.id == optionID:
                    opt.voterIDs.append(voterID)
                    return

    def unvoteOption(self, optionID: int, voterID: int):
        for opt in self.options:
            if opt.id == optionID and voterID in opt.voterIDs:
                opt.voterIDs.remove(voterID)
                return

    def savePoll(self, filepath: str):
        file = configparser.ConfigParser()
        file.read(filepath)
        if not file.has_section('META'):
            file.add_section('META')

        file.set('META', 'topic', self.topic)
        file.set('META', 'authorID', str(self.authorID))
        file.set('META', 'authorName', str(self.authorName))
        file.set('META', 'msgChannelID', str(self.msgChannelID))
        file.set('META', 'msgMessageID', str(self.msgMessageID))
        file.set('META', 'nextOptID', str(self.nextOptID))

        file.set('META', 'isClosed', str(misc.bool_to_int(self.isClosed)))
        file.set('META', 'custOpt', str(misc.bool_to_int(self.custOpt)))
        file.set('META', 'multiChoice', str(misc.bool_to_int(self.multiChoice)))

        for opt in self.options:
            if not file.has_section(opt.value):
                file.add_section(opt.value)
            file.set(opt.value, 'id', str(opt.id))
            file.set(opt.value, 'voterIDs', str(opt.voterIDs))

        with open(filepath, 'w') as configfile:
            file.write(configfile)

    def loadPoll(self, filepath: str):
        file = configparser.ConfigParser()
        file.read(filepath)
        self.topic = file['META']['topic']
        self.authorID = int(file['META']['authorID'])
        self.authorName = str(file['META']['authorName'])
        self.msgChannelID = int(file['META']['msgChannelID'])
        self.msgMessageID = int(file['META']['msgMessageID'])
        self.nextOptID = int(file['META']['nextOptID'])

        self.isClosed = misc.int_to_bool(int(file['META']['isClosed']))
        self.custOpt = misc.int_to_bool(int(file['META']['custOpt']))
        self.multiChoice = misc.int_to_bool(int(file['META']['multiChoice']))

        for section in file.sections():
            if section != 'META':
                newOpt = pollOption()
                newOpt.value = section
                newOpt.id = int(file[section]['id'])
                newOpt.voterIDs = [int(z) for z in re.findall('\d+', file[section]['voterIDs'])]
                self.addExOption(newOpt)

    def getOptID(self) -> int:
        self.nextOptID += 1
        return self.nextOptID - 1

    def hasVoted(self, voterID: int) -> bool:
        for opt in self.options:
            if opt.hasVoted(str(voterID)):
                return True
        return False

    def getOptPercentage(self, optionID: int) -> float:
        totalVotes = 0
        optVotes = 0
        for opt in self.options:
            totalVotes += len(opt.voterIDs)
            if opt.id == optionID:
                optVotes = len(opt.voterIDs)
        if totalVotes == 0:
            return 0
        return optVotes / totalVotes

    def getPollMsg(self, prefix: str) -> str:
        # This function is formatted for use with a discord bot

        # Title:
        pollTitle = f'Poll#-**{self.id}** by {self.authorName}\n'

        # isClosed:
        if self.isClosed:
            topicPre = 'diff\n- [CLOSED] '
        else:
            topicPre = 'diff\n+ '

        # Options to string:
        optStr = ''
        for opt in self.options:
            optStr += f'**{opt.id}**: {opt.value} **{len(opt.voterIDs)}%** ({int(self.getOptPercentage(opt.id)*100)})\n'

        # Clarifications:
        if not self.isClosed:
            clar = f'\nAbstimmen mit `{prefix}vote {self.id} <optionID>`'
        else:
            clar = '\nPoll has been closed.'
        optStr += clar

        msg = f'{pollTitle}```{topicPre}{self.topic}```\n{optStr}'

        return msg
