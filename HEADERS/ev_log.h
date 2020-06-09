#ifndef EV_LOG_H
#define EV_LOG_H
#include <iostream>
#include <string>
#include <list>
#include <fstream>
#include "../SOURCES/miscCode.cpp"

class ev_log
{
public:
    enum Level {
        INFO,
        WARNING,
        ERROR,
        SLEEPY_ERROR,
        DEBUG
    };

    ev_log(const std::string filePath = "", int maxBufferSize = 50) {
        init(filePath, maxBufferSize);
    };

    void init(const std::string filePath = "", int maxBufferSize = 50){
        this->filePath = filePath;
        this->maxBufferSize = maxBufferSize;
        loadBuffer();
    }

    void log(const std::string& message, Level level = INFO);
    std::string getCurrTime();

    std::list<std::string> getRecentEvents(const unsigned int eventCount = 10);
    int getMaxBufferSize() const {return maxBufferSize;};
    int getCurrBufferSize() const {return logBuffer.size();};

private:
    void loadBuffer();
    std::string levelToStr(Level level);
    int maxBufferSize;
    std::list<std::string> logBuffer;
    std::string filePath;
};
#endif // EVENT_LOG_H
