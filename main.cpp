#include "dc_botClient.h"

int main()
{
    std::string token = getToken();
    dc_botClient comClient(token,2);
    comClient.run();


}
