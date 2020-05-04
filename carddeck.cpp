#include "carddeck.h"

void cardDeck::importCards(const std::string &directoryPath)
{
    //Import white cards:
    std::ifstream whiteFile;
    whiteFile.open(directoryPath + "/white.txt");
    if(!whiteFile.is_open()){return;}

    cardStack wCards;
    while(!whiteFile.eof()){
        std::string currLine;
        std::getline(whiteFile, currLine);
        card currCard;
        currCard.black = false;
        currCard.text = currLine;
        wCards.addCard(currCard);
    }
    whiteFile.close();

    //import black cards:
    std::ifstream blackFile;
    blackFile.open(directoryPath + "/white.txt");
    if(!blackFile.is_open()){return;}

    cardStack bCards;
    while(!blackFile.eof()){
        std::string currLine;
        std::getline(blackFile, currLine);
        card currCard;
        currCard.black = true;
        currCard.text = currLine;
        bCards.addCard(currCard);
    }
    blackFile.close();

    //Save stacks:
    deckName = directoryPath;//Change this to something better
    whiteCards = wCards;
    blackCards = bCards;
}
