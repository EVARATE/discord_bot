#include "com_rules.h"

void com_rules::execute(SleepyDiscord::Message message)
{
    //Read message:
    SleepyDiscord::Message ruleMessage = parent.getMessage(ruleChannelID, ruleMessageID);
    //Send rules:
    parent.sendMessage(message.channelID, ruleMessage.content);
    //Log:
    parent.to
}
