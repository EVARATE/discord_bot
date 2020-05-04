#ifndef CARDSTACK_H
#define CARDSTACK_H
#include <vector>
#include <string>
#include <algorithm>
#include <random>

typedef struct{
    bool black;
    std::string text;
}card;

class cardStack
{
public:
    void addCard(card& card);
    void addCard(bool& black, const std::string& text);
    void removeCard(const std::string& text);
    void addStack(cardStack& newStack);

    void shuffle();

    unsigned int size() {return cards.size();};
    void resize(int size) {cards.resize(size);};
    void push_back(card& newCard) {cards.push_back(newCard);};
    void pop_back() {cards.pop_back();};

    card& operator[](unsigned int i) {return cards[i];};

private:
    std::vector<card> cards;

};

#endif // CARDSTACK_H
