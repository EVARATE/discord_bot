#ifndef COM_RULES_H
#define COM_RULES_H
#include "discordcommand.h"

class com_rules: public discordCommand
{
public:
    void execute(SleepyDiscord::Message message);
private:
    std::string ruleChannelID = "702501123218604102";
    std::string ruleMessageID = "702501801047621681";
};

#endif // COM_RULES_H
