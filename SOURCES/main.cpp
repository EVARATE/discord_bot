#include "../HEADERS/dc_botClient.h"
#include <unistd.h>
int main()
{
    ev_log evLog(configPath + "log.txt", 50);
    std::string token = getToken();
    dc_botClient comClient(token,SleepyDiscord::USER_CONTROLED_THREADS);
    comClient.preInit(evLog);
    comClient.run();

}
