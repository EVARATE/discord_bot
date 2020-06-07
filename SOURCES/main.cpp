#include "../HEADERS/dc_botClient.h"

int main()
{
    std::string token = getToken();
    dc_botClient comClient(token,SleepyDiscord::USER_CONTROLED_THREADS);
    comClient.userInit();
    comClient.run();
}
