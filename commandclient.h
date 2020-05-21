#ifndef COMMANDCLIENT_H
#define COMMANDCLIENT_H
#include "sleepy-discord/include/sleepy_discord/websocketpp_websocket.h"
#include "sleepy-discord/include/sleepy_discord/client.h"
#include "sleepy-discord/include/sleepy_discord/server.h"
#include "miscCode.cpp"


class commandClient : public SleepyDiscord::DiscordClient{
public:
    using SleepyDiscord::DiscordClient::DiscordClient;
    //Session actions
    void onMessage(SleepyDiscord::Message message);
    void onReady(std::string* jsonMessage);
    void onDisconnect();
    void onResume();

    //Commands
    void execTextCommand(stringVec& command, SleepyDiscord::Message& message);
    void respondTextCommand(textCommand& command, const std::string& channelID);
    void com_rules(SleepyDiscord::Message& message);
    void com_help(SleepyDiscord::Message& message);
    void com_prefix(SleepyDiscord::Message& message);
    void com_random(SleepyDiscord::Message& message);
    void com_reloadCommands();
    void com_log(SleepyDiscord::Message& message);

    //Other
    void loadTextCommands();
    void updateHelpMsg();
    void toLog(const std::string& text, int status = 0);//Status: 0='normal', 1='only in discord'

private:
    //Data:
    std::string prefix = "t/";
    std::string help_msg;
    std::vector<textCommand> lectureCommands;
    stringVec offlineLogBuffer;
    bool isConnected;

    //IDs:
    std::string ruleChannelID = "702501123218604102";
    std::string ruleMessageID = "702501801047621681";
    std::string logChannelID = "712643802996932648";

    //TRIGGERS:
    stringVec trig_rules = {"rules", "regeln"};
    stringVec trig_help = {"help", "hilfe"};
    stringVec trig_prefix = {"setprefix"};
    stringVec trig_random = {"random"};
    stringVec trig_relComs = {"reloadcmds"};
    stringVec trig_log = {"log"};

};
#endif // COMMANDCLIENT_H



