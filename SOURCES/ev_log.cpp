#include "../HEADERS/ev_log.h"

void ev_log::log(const std::string &message, Level level){
    // [dd/mm/yy hh/mm/ss] LEVEL: <message>

    std::string eventMsg = "[" + getCurrTime() + "] " + levelToStr(level) + ": " + message;

    //Log to console:
    fprintf(stderr, (eventMsg + "\n").c_str());

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
void ev_log::loadBuffer(){
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
std::string ev_log::levelToStr(Level level){
    int lev = static_cast<int>(level);
    switch (lev) {
    case 0:
        return "INFO";
    case 1:
        return "WARNING";
    case 2:
        return "ERROR";
    case 3:
        return "SLEEPY_ERROR";
    case 4:
        return "DEBUG";
    default:
        return "INFO";
    }
}
std::string ev_log::getCurrTime(){
    return getTimeStr(time(0));
}
std::list<std::string> ev_log::getRecentEvents(const unsigned int eventCount){
    if(eventCount >= logBuffer.size() || logBuffer.size() == 0){
        return  logBuffer;
    }
    else{
        std::list<std::string> evList;
        unsigned int i = 0;
        bool a = true;
        for(auto it = logBuffer.end(); it != logBuffer.begin(); --it){
            if(a){--it; a = false;}
            evList.push_front(*it);
            ++i;
            if(i >= eventCount){
                break;
            }
        }
        return evList;
    }
}
