#include "cahplaysession.h"


void CAHplaySession::addPlayer(CAHplayer &newPlayer)
{
    players.push_back(newPlayer);
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
    for(int i = 0; i < maxRounds; ++i){
        determineCzar(i);
        assignPlayerActions();

    }
    gameRunning = false;
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

void CAHplaySession::assignPlayerActions()
{

}

void CAHplaySession::determineCzar(int roundCount)
{
    int index;
    if((int)players.size() < roundCount){
        index = players.size() % roundCount;
    }else{
        index = roundCount;
    }

    //Unset czar for every player except the determined one
    for(int i = 0; i < (int)players.size(); ++i){
        if(i == index){
            players[i].setCzar(true);
        }else{
            players[i].setCzar(false);
        }
    }
}
