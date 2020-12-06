class pollOption:
    id = -1
    voteCount = 0
    value = ''
    voterIDs = []

    def hasVoted(self, voterID: str) -> bool:
        for ID in self.voterIDs:
            if ID == voterID:
                return True
        return False


class poll:
    def __init__(self, question: str, options: list):
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
        if (not self.hasVoted(voterID)) or self.MultiChoice:
            for opt in self.options:
                if opt.id == optionID:
                    if not opt.hasVoted(voterID):
                        opt.voteCount += 1
                        opt.voterIDs.append(voterID)
                        return

    def unvoteOption(self, optionID: int, voterID: int):
        if self.hasVoted(voterID):
            for opt in self.options:
                if opt.id == optionID and opt.hasVoted(voterID):
                    opt.voteCount -= 1
                    opt.voterIDs.remove(voterID)
                    return

    # def savePoll(self):

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
        voteSum = 0
        optCount = 0
        for opt in self.options:
            voteSum += opt.voteCount
            if opt.id == optionID:
                optCount = opt.voteCount
        if optCount * voteSum == 0:
            ret = 0
        else:
            ret = optCount / voteSum
        return ret

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
            optStr += '{0}: **{1}** ({2}) {3}%\n'.format(opt.id, opt.value, opt.voteCount, self.getOptPercentage(opt.id))

        msg = '{0}```{1}{2}```\n{3}'.format(pollTitle, topicPre, self.topic, optStr)
        return msg

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
