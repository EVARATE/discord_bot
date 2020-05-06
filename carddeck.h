#ifndef CARDDECK_H
#define CARDDECK_H

#include "cardstack.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <regex>


class cardDeck
{
public:

    void importCards(const std::string& directory);

    std::string deckName = "unnamed Deck";

    cardStack whiteCards;
    cardStack blackCards;
};

#endif // CARDDECK_H
