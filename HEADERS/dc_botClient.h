#ifndef COMMANDCLIENT_H
#define COMMANDCLIENT_H
#include "../deps/sleepy-discord/include/sleepy_discord/websocketpp_websocket.h"
#include "poll.h"
#include "ev_log.h"


class dc_botClient : public SleepyDiscord::DiscordClient{
public:
    using SleepyDiscord::DiscordClient::DiscordClient;

    void userInit();//Call this before anything else

    //Session actions
    void onMessage(SleepyDiscord::Message message) override;
    void onReady(SleepyDiscord::Ready readyData) override;
    void onDisconnect() override;
    void onResume() override;
    void onError(SleepyDiscord::ErrorCode errorCode, const std::string errorMessage) override;

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
    void com_quote(SleepyDiscord::Message& message);
    void com_updhelp(SleepyDiscord::Message& message);
    void com_getLog(SleepyDiscord::Message& message);

    //Other
    void loadTextCommands();
    void updateHelpMsg();
    void updateIPInfo();
    int getPollID();
    void updatePollData(const int pollID);
    void loadAllPolls();
    void savePoll(mo_poll& poll);

private:
    //Log:
    ev_log evLog;

    //Data:
    std::string prefix = "/";
    std::string help_msg;
    std::vector<textCommand> lectureCommands;
    stringVec offlineLogBuffer;
    std::vector<mo_poll> polls;
    int nextPollID = 0;

    //IDs:
    std::string ruleChannelID = "702501123218604102";
    std::string ruleMessageID = "702501801047621681";
    std::string logChannelID =  "712643802996932648";

    //TRIGGERS:
    Ctrigger trig_rules {"rules", "regeln"};
    Ctrigger trig_help = {"help", "hilfe"};
    Ctrigger trig_prefix = {"setprefix"};
    Ctrigger trig_random = {"random"};
    Ctrigger trig_relComs = {"reloadcmds"};
    Ctrigger trig_log = {"log"};
    Ctrigger trig_ip = {"ip"};
    Ctrigger trig_poll = {"poll", "vote", "unvote",
                           "polladd", "pollrem", "pollclose",
                           "pollset", "custopt", "multi"};
    Ctrigger trig_quote = {"quote"};
    Ctrigger trig_updHelp = {"updhelp"};
    Ctrigger trig_getlog = {"getlog", "file"};

    std::vector<Ctrigger> triggerList = {trig_rules, trig_help, trig_prefix,
                                         trig_random, trig_relComs, trig_log,
                                         trig_ip, trig_poll, trig_quote,
                                        trig_updHelp, trig_getlog};

};
#endif // COMMANDCLIENT_H



