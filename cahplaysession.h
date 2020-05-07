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
    std::string getCzar();

    //Card actions:
    std::string getCurrBlackCard();
    cardStack getPlayerStack(const std::string& playerName);
    void getPlayerStack(const std::string& playerName, cardStack& stack);

    //Other:
    void setGameID(int id) {gameID = id;};
    int getGameID() {return gameID;};
    void setRunning(bool state);
    bool isRunning();


    std::vector<CAHplayer> players;
    std::vector<cardDeck> decks;//Mixing multiple decks is possible

    //Settings:
    int maxRounds = 5;
    int cardsPerPlayer = 8;
    int cardsPlayable = 1;//How many cards can be played at once
    
    //Unused cards:
    cardStack whiteCards;
    cardStack blackCards;
    cardStack chosenCards;

    //Played cards:
    cardStack whitePlayed;
    cardStack blackPlayed;

    //Game info:
    bool gameRunning = false;
    bool roundRunning = false;
    int gameID;
};

#endif // CAHPLAYSESSION_H
