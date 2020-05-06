#include "cardstack.h"


void cardStack::addCard(card &card)
{
    cards.push_back(card);
}

void cardStack::addCard(bool &black, const std::string &text)
{
    card newCard;
    newCard.black = black;
    newCard.text = text;
    addCard(newCard);
}

void cardStack::removeCard(const std::string &text)
{
    for(auto it = cards.begin(); it != cards.end(); ++it){
        if(it->text == text){
            cards.erase(it);
            break;
        }
    }
}

void cardStack::addStack(cardStack &newStack)
{
    for(int i = 0; i < (int)newStack.size(); ++i){
        addCard(newStack.cards[i]);
    }
}

void cardStack::shuffle()
{
    static auto rng = std::default_random_engine {};
    std::shuffle(std::begin(cards), std::end(cards), rng);
}
