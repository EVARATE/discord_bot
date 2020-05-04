#ifndef CAHPLAYER_H
#define CAHPLAYER_H
#include "cardstack.h"

class CAHplayer
{
public:

    void setCzar(bool state) {czar = state;};

    std::string name;
    bool czar;
    cardStack handCards;
};

#endif // CAHPLAYER_H
