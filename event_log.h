#ifndef EVENT_LOG_H
#define EVENT_LOG_H
#include <iostream>
#include <string>
#include <list>
#include <fstream>

class event_log
{
public:
    enum Level {
        INFO,
        WARNING,
        ERROR,
        DEBUG,
        BAD_INPUT
    };

    event_log(const std::string filePath = "", int maxBufferSize = 50) {
        this->filePath = filePath;
        this->maxBufferSize = maxBufferSize;
        loadBuffer();
    };
    event_log();

    void init(const std::string filePath = "", int maxBufferSize = 50){
        this->filePath = filePath;
        this->maxBufferSize = maxBufferSize;
        loadBuffer();
    }

    void log(const std::string& message, Level level = INFO);
    std::string getCurrTime();

    std::list<std::string> getRecentEvents(const int eventCount = 10);


private:
    void loadBuffer();
    std::string levelToStr(Level level);
    int maxBufferSize;
    std::list<std::string> logBuffer;
    std::string filePath;
};
#endif // EVENT_LOG_H
