#include "../HEADERS/dc_botClient.h"
#include <unistd.h>
int main()
{
    ev_log evLog(configPath + "log.txt", 50);
    int crashCounter = 0;
    while(true){
        try {
            std::string token = getToken();
            dc_botClient comClient(token,SleepyDiscord::USER_CONTROLED_THREADS);
            comClient.preInit(evLog);
            comClient.run();
        } catch (...) {
            crashCounter++;
            evLog.log("PROGRAM CRASH #" + std::to_string(crashCounter) + ". RESTARTING...", ev_log::Level::ERROR);
        }
        usleep(1000000);//Sleep one second before retrying
    }
}
