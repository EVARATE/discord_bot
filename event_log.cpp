#include "event_log.h"

void event_log::log(std::string &message, Level level){
    // [dd/mm/yy hh/mm/ss]: LEVEL: <message>

    std::string eventMsg = "[" + getCurrTime() + "] " + levelToStr(level) + ": " + message;

    //Push eventMsg into logBuffer
    logBuffer.push_back(eventMsg);
    while((int)logBuffer.size() > maxBufferSize){
        logBuffer.erase(logBuffer.begin());
    }

    //Save to file if path exists:
    if(filePath.size() > 0){
        std::ofstream ofile;
        ofile.open(filePath, std::ios::app);
        if(ofile.is_open()){
            ofile << eventMsg << "\n";
            ofile.close();
        }
    }
}
void event_log::loadBuffer(){
    //Load last events into buffer if they exist:
    if(filePath.size() > 0){
        std::ifstream ifile;
        ifile.open(filePath);
        if(ifile.is_open()){
            std::string line;
            while(getline(ifile, line)){
                logBuffer.push_back(line);
                if((int)logBuffer.size() > maxBufferSize){
                    logBuffer.erase(logBuffer.begin());
                }
            }
        }
    }
}
std::string event_log::levelToStr(Level level){
    int lev = static_cast<int>(level);
    switch (lev) {
    case 0:
        //INFO
        return "INFO";
    case 1:
        //WARNING
        return "WARNING";
    case 2:
        //ERROR
        return "ERROR";
    case 3:
        //DEBUG
        return "DEBUG";
    default:
        return "INFO";
    }
}
std::string event_log::getCurrTime(){
    time_t now = time(0);
    tm *ltm = localtime(&now);
    return std::to_string(ltm->tm_mday) + "/" + std::to_string(1 + ltm->tm_mon) + "/" + std::to_string(1900 + ltm->tm_year).substr(2, 3) + " " +
           std::to_string(1 + ltm->tm_hour) + ":" + std::to_string(ltm->tm_min) + ":" + std::to_string(ltm->tm_sec);
}
std::list<std::string> event_log::getRecentEvents(const int eventCount){

}
