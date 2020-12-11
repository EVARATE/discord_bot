import configparser

class pollOption:
    def __init__(self):
        self.voterIDs = []
    id = -1
    value = ''
    voterIDs = []

    def hasVoted(self, voterID: str) -> bool:
        if voterID in self.voterIDs:
            return True
        return False


class poll:
    id = -1
    topic = ''
    options = []

    # Metadata:
    authorName = ''
    authorID = -1
    msgChannelID = -1
    msgMessageID = -1
    isClosed = False
    custOpt = False
    MultiChoice = False

    nextOptID = 1

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

    # def savePoll(self, filepath: str):
        # Format:
        #
        # [METADATA]
        # topic = My topic
        #
        # authorName = ''
        # authorID = -1
        # msgChannelID = -1
        # msgMessageID = -1
        # isClosed = False
        # custOpt = False
        # MultiChoice = False
        # nextOptID = 1
        #
        # [Option_1]
        # value = My option value
        # IDs = 1234567890, 1234567890, ...
        #
        # [Option_2]
        # value = ...
        # IDs = ...

        # return

    # def loadPoll(self):

    def getOptID(self) -> int:
        self.nextOptID += 1
        return self.nextOptID - 1

    def hasVoted(self, voterID: int) -> bool:
        for opt in self.options:
            if opt.hasVoted(voterID):
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
        return optVotes/totalVotes


    def getPollMsg(self) -> str:
        # This function is formatted for use with a discord bot

        # Poll#<pollNr> by <author>
        # ```
        # The poll topic
        # ```
        # 1. **Option 1**
        # 2. **Option 2**
        # 3. **Option 3**
        #
        # Settings: [none, custOpt, multi, ...]

        # Title:
        pollTitle = 'Poll#-**{0}** by {1}\n'.format(self.id, self.authorName)

        # isClosed:
        if self.isClosed:
            topicPre = 'diff\n- [CLOSED] '
        else:
            topicPre = 'diff\n+ '

        # Options to string:
        optStr = ''
        for opt in self.options:
            optStr += '{0}: **{1}** ({2}) {3}%\n'.format(opt.id,
                                                         opt.value,
                                                         len(opt.voterIDs),
                                                         self.getOptPercentage(opt.id)*100.)

        msg = '{0}```{1}{2}```\n{3}'.format(pollTitle, topicPre, self.topic, optStr)
        return msg

