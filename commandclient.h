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

    //Other
    void loadTextCommands();

private:
    //Data:
    std::string prefix = "t/";
};  std::vector<textCommand> textCommands;

#endif // COMMANDCLIENT_H
