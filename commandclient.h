#ifndef COMMANDCLIENT_H
#define COMMANDCLIENT_H
#include "sleepy-discord/include/sleepy_discord/websocketpp_websocket.h"
#include "sleepy-discord/include/sleepy_discord/client.h"
#include "sleepy-discord/include/sleepy_discord/server.h"
#include "cahplaysession.h"
#include <vector>
#include <iterator>
#include <string>
#include <regex>
#include <random>
#include <thread>
#include <chrono>
#include <ctime>

typedef std::vector<std::string> stringVec;

typedef struct{
    int weekday;//1-7: Mon-Sun
    int day;
    int month;//1-12: Jan-Dec
    int year;

    int second;
    int minute;
    int hour;
}timeObj;

typedef struct{
    std::string name = "unbekannt";
    std::string termin1 = "unbekannt";
    std::string termin2 = "unbekannt";
    std::string klausur = "unbekannt";
    std::string nachklausur = "unbekannt";
    std::string zoomDaten = "unbekannt";
}vorlesung;



class commandClient : public SleepyDiscord::DiscordClient {
public:
    using SleepyDiscord::DiscordClient::DiscordClient;
    void onMessage(SleepyDiscord::Message message);

    //Access:
    SleepyDiscord::Channel              channelByName(std::string channelName);
    SleepyDiscord::User                 userByName(std::string userName);
    SleepyDiscord::User                 userByNick(std::string userNick);
    std::vector<SleepyDiscord::User>    usersInChannel(std::string channelID);
    std::vector<SleepyDiscord::User>    usersWithRole(std::string roleName);
    bool                                userHasRole(std::string userID, std::string roleName);
    std::string getRuleMsg();

    //Actions
    void toConsoleLog(const std::string &text);
    void setupData();
    void updateHelpMsg();
    timeObj getCurrentTime();

    //Other
    void addLecture(const std::string& name,
                    const std::string& termin1,
                    const std::string& termin2,
                    const std::string& klausur,
                    const std::string& nachklausur,
                    const std::string& zoomDaten);
    //Commands
    void sendRulesMsg(SleepyDiscord::Message message);
    void sendHelpMsg(SleepyDiscord::Message message);
    void setPrefix(std::string newPrefix);
    void sendRandom(SleepyDiscord::Message message, std::string rawOptions);
    void sendLectureInfo(SleepyDiscord::Message message, std::string name);
    void sendDirMessage(const std::string& userName, const std::string& text);

    //CAH:
    void CAH_processInput(stringVec& command, SleepyDiscord::Message message);
    void CAH_createGame(int gameID);
    void CAH_loadDeck(const std::string& deckName, int gameID);
    void CAH_addPlayer(const std::string& playerName, int gameID);
    void CAH_removePlayer(const std::string& playerName, int gameID);
    void CAH_startNewRound(int gameID);
    void CAH_updatePlayerHands(int gameID);
    void CAH_playCards(SleepyDiscord::Message message, stringVec cardsPlayed);
    bool CAH_isPlaying(const std::string& playerName);

    CAHplaySession CAH_getGame(int gameID);
    CAHplaySession CAH_getGame(const std::string& playerName);
    void CAH_getGameRef(int gameID, CAHplaySession& session);
    void CAH_getGameRef(std::string playerName, CAHplaySession& session);
    int CAH_getGameID();


private:
    //Vorlesungen:
    std::vector<vorlesung> vorlesungen;

    //Bot options:
    std::string prefix = "t/";
    std::string helpMessage = "";

    //Server:
    const std::string serverID = "541324032042205196";
    //Important messages:
    std::string ruleMessageID = "702501801047621681";
    std::string helpMessageID = "702969362679857283";

    //CAH:
    std::vector<CAHplaySession> CAH_sessions;
    std::vector<std::string> CAH_activePlayers;
    int nextCAHID = 0;
    std::string CAH_deckLocation = "/media/mo/Qt_Projects/discord_bot/CAH_decks/";

};

#endif // COMMANDCLIENT_H
