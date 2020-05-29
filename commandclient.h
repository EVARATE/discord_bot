#ifndef COMMANDCLIENT_H
#define COMMANDCLIENT_H
#include "sleepy-discord/include/sleepy_discord/websocketpp_websocket.h"
#include "sleepy-discord/include/sleepy_discord/client.h"
#include "sleepy-discord/include/sleepy_discord/server.h"
#include "poll.h"


class commandClient : public SleepyDiscord::DiscordClient{
public:
    using SleepyDiscord::DiscordClient::DiscordClient;
    //Session actions
    void onMessage(SleepyDiscord::Message message);
    void onReady(std::string* jsonMessage);
    void onDisconnect();
    void onResume();
    void onError(SleepyDiscord::ErrorCode errorCode, const std::string errorMessage);

    //Commands
    void execTextCommand(stringVec& command, SleepyDiscord::Message& message);
    void respondTextCommand(textCommand& command, const std::string& channelID);
    void com_rules(SleepyDiscord::Message& message);
    void com_help(SleepyDiscord::Message& message);
    void com_prefix(SleepyDiscord::Message& message);
    void com_random(SleepyDiscord::Message& message);
    void com_reloadCommands();
    void com_log(SleepyDiscord::Message& message);
    void com_ip(SleepyDiscord::Message& message);
    void com_poll(SleepyDiscord::Message& message);
    void com_vote(SleepyDiscord::Message& message);
    void com_unvote(SleepyDiscord::Message& message);
    void com_pollAdd(SleepyDiscord::Message& message);
    void com_pollRem(SleepyDiscord::Message& message);
    void com_pollSet(SleepyDiscord::Message& message);
    void com_pollClose(SleepyDiscord::Message& message);

    //Other
    void loadTextCommands();
    void updateHelpMsg();
    void toLog(const std::string& text, int status = 0);//Status: 0='normal', 1='only in discord'
    void updateIPInfo();
    int getPollID();
    void updatePollData(const int pollID);
    void loadAllPolls();
    void savePoll(mo_poll& poll);

private:
    //Data:
    std::string prefix = "t/";
    std::string help_msg;
    std::vector<textCommand> lectureCommands;
    stringVec offlineLogBuffer;
    bool isConnected;
    std::vector<mo_poll> polls;
    int nextPollID = 0;

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
    stringVec trig_ip = {"ip"};
    stringVec trig_poll = {"poll", "vote", "unvote",
                           "polladd", "pollrem", "pollclose",
                           "pollset", "custopt_", "multi_"};

};
#endif // COMMANDCLIENT_H



