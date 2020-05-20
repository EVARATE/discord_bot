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

    //Other
    void loadTextCommands();
    void toLog(const std::string& text);

private:
    //Data:
    std::string prefix = "t/";
    std::vector<textCommand> textCommands;
    stringVec offlineLogBuffer;
    bool isConnected;
};
#endif // COMMANDCLIENT_H
