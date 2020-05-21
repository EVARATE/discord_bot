#ifndef DISCORDCOMMAND_H
#define DISCORDCOMMAND_H
#include "sleepy-discord/include/sleepy_discord/websocketpp_websocket.h"
#include "sleepy-discord/include/sleepy_discord/client.h"
#include "sleepy-discord/include/sleepy_discord/server.h"
#include "miscCode.cpp"

/* This class serves as a blueprint for chat commands. When implementing
 * a new chat command, a new class is created which inherits this class.
 * The 'execute()' method can be redefined for each command.
 *
 * There are some predefined methods which are supposed to make it easier
 * to work with the discord client.
 */

class discordCommand
{
public:
    discordCommand(stringVec commands, commandClient& Parent) :
        triggers(commands), parent(Parent) {}
    void execute();



    stringVec triggers;
    SleepyDiscord::DiscordClient& parent;
};

#endif // DISCORDCOMMAND_H
