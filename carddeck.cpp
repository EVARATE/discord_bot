#include "carddeck.h"

inline std::vector<std::string> returnMatches(std::string str, std::regex reg){
    std::vector<std::string> sVec;
    std::sregex_iterator currentMatch(str.begin(), str.end(), reg);
    std::sregex_iterator lastMatch;
    while(currentMatch != lastMatch){
        std::smatch match = *currentMatch;
        sVec.push_back(match.str());
        currentMatch++;
    }
    return sVec;
}

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
    blackFile.open(directoryPath + "/black.txt");
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

    //deck name from path:
    std::regex nameReg("[^/]+");
    std::vector<std::string> path = returnMatches(directoryPath, nameReg);
    //Save stacks:
    deckName = path[path.size() - 1];
    whiteCards = wCards;
    blackCards = bCards;
}
