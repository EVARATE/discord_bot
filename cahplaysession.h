#ifndef CAHPLAYSESSION_H
#define CAHPLAYSESSION_H
#include "carddeck.h"
#include "cahplayer.h"



class CAHplaySession
{
public:

    //Players:
    void addPlayer(CAHplayer& newPlayer);
    void addPlayer(const std::string& playerName);
    void removePlayer(const std::string& name);
    CAHplayer playerByName(const std::string& playerName);
    bool playerExists(const std::string& playerName);
    //Decks:
    void addDeck(cardDeck& newDeck);
    void removeDeck(const std::string& deckName);

    //Session actions:
    void startGame();
    void initCards();
    void shufflePlayers();
    void distributeCards();
    void determineCzar(int roundCount);

    //Card actions:

    //Other:
    void setGameID(int id) {gameID = id;};
    int getGameID() {return gameID;};



    std::vector<CAHplayer> players;
    std::vector<cardDeck> decks;//Mixing multiple decks is possible

    //Settings:
    int maxRounds = 5;
    int cardsPerPlayer = 8;
    
    //Unused cards:
    cardStack whiteCards;
    cardStack blackCards;

    //Played cards:
    cardStack whitePlayed;
    cardStack blackPlayed;

    //Game info:
    bool gameRunning = false;
    int gameID;
};

#endif // CAHPLAYSESSION_H
