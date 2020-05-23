#include <iostream>
#include <fstream>
#include "commandclient.h"

int main()
{
    std::string token = getToken();
    commandClient comClient(token,2);
    comClient.run();


}
