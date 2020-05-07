#include "cahplaysession.h"


void CAHplaySession::addPlayer(CAHplayer &newPlayer)
{
    //See if player already exists:
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == newPlayer.name){
            return;
        }
    }
    players.push_back(newPlayer);
}

void CAHplaySession::addPlayer(const std::string &playerName)
{
    CAHplayer newPlayer;
    newPlayer.name = playerName;
    newPlayer.czar = false;
    addPlayer(newPlayer);
}

void CAHplaySession::removePlayer(const std::string &name)
{
    //Get player:
    CAHplayer thisPlayer = playerByName(name);
    //Put cards to 'played' stack:
    for(int i = 0; i < (int)thisPlayer.handCards.size(); ++i){
        whitePlayed.push_back(thisPlayer.handCards[i]);
    }

    //Delete Player:
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == name){
            players.erase(it);
            break;
        }
    }
}

CAHplayer CAHplaySession::playerByName(const std::string &playerName)
{
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == playerName){
            return *it;
        }
    }
    return CAHplayer();
}

bool CAHplaySession::playerExists(const std::string &playerName)
{
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == playerName){
            return true;
        }
    }
    return false;
}

void CAHplaySession::addDeck(cardDeck &newDeck)
{
    decks.push_back(newDeck);
}

void CAHplaySession::removeDeck(const std::string &deckName)
{
    if(gameRunning){return;}
    for(auto it = decks.begin(); it != decks.end(); ++it){
        if(it->deckName == deckName){
            decks.erase(it);
            break;
        }
    }
}

void CAHplaySession::startGame()
{
    gameRunning = true;
    initCards();
    distributeCards();
    shufflePlayers();
    //First player is Czar:
    players[0].setCzar(true);
}

void CAHplaySession::initCards()
{

    //Combine all decks:
    for(int i = 0; i < (int)decks.size(); ++i){
        whiteCards.addStack(decks[i].whiteCards);
        blackCards.addStack(decks[i].blackCards);
    }
    //Shuffle all decks:
    whiteCards.shuffle();
    blackCards.shuffle();

    //Clear all played cards:
    whitePlayed.resize(0);
    blackPlayed.resize(0);
}

void CAHplaySession::shufflePlayers()
{
    static auto rng = std::default_random_engine {};
    std::shuffle(std::begin(players), std::end(players), rng);
}

void CAHplaySession::distributeCards()
{
    //Every player gets 'cardsPerPlayer' many cards from the top of the deck:
    for(int i = 0; i < (int)players.size(); ++i){
        for(int j = 0; j < cardsPerPlayer; ++j){
            players[i].handCards.addCard(whiteCards[whiteCards.size() - 1]);
            whiteCards.pop_back();
        }
    }
}

std::string CAHplaySession::getCzar()
{
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->czar){
            return it->name;
        }
    }
    return "Uh, no one I guess...";
}

std::string CAHplaySession::getCurrBlackCard()
{
    return blackCards[blackCards.size() - 1].text;
}

cardStack CAHplaySession::getPlayerStack(const std::string &playerName)
{
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == playerName){
            return it->handCards;
        }
    }
    return cardStack();
}

void CAHplaySession::getPlayerStack(const std::string &playerName, cardStack &stack){
    for(auto it = players.begin(); it != players.end(); ++it){
        if(it->name == playerName){
            stack = it->handCards;
        }
    }
}

void CAHplaySession::setRunning(bool state)
{
    roundRunning = state;
}

bool CAHplaySession::isRunning()
{
    return roundRunning;
}
