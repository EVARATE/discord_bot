#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <regex>
#include <ctime>
#include <chrono>
#include <stdlib.h>
#include <cstdlib>


//=====CONSTANTS=====

const std::string homeDir(getenv("HOME"));
const std::string configPath = homeDir + "/.config/discord_bot/";

//=====TYPEDEFS=====
typedef std::vector<std::string> stringVec;

typedef struct{
    int weekday;//1-7: Mon-Sun
    int day;
    int month;//1-12: Jan-Dec
    int year;

    int second;
    int minute;
    int hour;
}timeObj;

typedef struct{
    std::string name;
    std::string value;
}property;

typedef struct{
    stringVec triggers;//Multiple commands can trigger this
    std::vector<property> properties;
}textCommand;

//=====FUNCTIONS=====
inline std::string getToken(){
    std::string token;
    std::ifstream ifile;
    ifile.open(configPath + "token.txt");
    if(!ifile.is_open()){
        //Enter token manually:
        std::cout << "Couldn't read 'token.txt'.\n";
        bool invalidToken;
        do{
            std::cout << "Enter token: ";

            std::cin >> token;
            if(token.length() == 59){
                invalidToken = false;
            }else{
                std::cout << "Invalid token!\n";
                invalidToken = true;
            }
        }while(invalidToken);
        //Save token to file:
        std::ofstream ofile;
        ofile.open(configPath + "token.txt");
        if(ofile.is_open()){
            ofile << token;
            ofile.close();
            return token;
        }else{
            std::cout << "Couldn't save token to token.txt\n";
            return token;
        }
    }else{
        ifile >> token;
        if(token.length() == 59){
            return token;
        }else{
            std::cout << "Invalid token!\n";
            return "";
        }
    }

}
inline std::string toLowerCase(std::string str){
    std::transform(str.begin(), str.end(), str.begin(), [](unsigned char c){return std::tolower(c);});
    return str;
}
inline std::string removeSpaces(std::string& str){
    std::remove(str.begin(), str.end(), ' ');
    return str;
}
inline stringVec returnMatches(std::string str, std::regex reg){
    stringVec sVec;
    std::sregex_iterator currentMatch(str.begin(), str.end(), reg);
    std::sregex_iterator lastMatch;
    while(currentMatch != lastMatch){
        std::smatch match = *currentMatch;
        sVec.push_back(match.str());
        currentMatch++;
    }
    return sVec;
}
inline stringVec strToWords(std::string str){
    std::regex reg("[^ ]+");
    return returnMatches(str, reg);
}
inline void addHelpEntry(std::string& msg, std::string& prefix, const std::string& name, stringVec& triggers){
    msg.append("*" + name + ":* ");
    for(auto it = triggers.begin(); it != triggers.end(); ++it){
        msg.append("`" + prefix + *it + "`, ");
    }
    //Delete last characters ', '
    msg.pop_back();
    msg.pop_back();
    msg.append("\\n");
}
inline timeObj getCurrentTime(){
        auto rawTime = std::chrono::system_clock::now();
        std::time_t currTime = std::chrono::system_clock::to_time_t(rawTime);
        std::string time = std::ctime(&currTime);

        //Interpret output:
        std::regex allReg("[^ ]+");
        stringVec matches = returnMatches(time, allReg);

        //Example format: Mon Oct  2 00:59:08 2017
        timeObj currentTime;

        //Weekday:
        stringVec weekdays = {"Mon","Tue","Wed","Thu","Fri","Sat","Sun"};
        for(int i = 0; i < (int)weekdays.size(); ++i){
            if(matches[0] == weekdays[i]){
                currentTime.weekday = i + 1;
                break;
            }
        }
        //Day:
        currentTime.day = std::stoi(matches[2]);
        //Month:
        stringVec months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
        for(int i = 0; i < (int)months.size(); ++i){
            if(months[i] == matches[1]){
                currentTime.month = i + 1;
                break;
            }
        }
        //Year
        currentTime.year = std::stoi(matches[4]);

        //Time:
        std::regex timeReg("\\d+");
        stringVec timeStrings = returnMatches(matches[3], timeReg);
        //Format: hh:mm:ss
        //Second:
        currentTime.second = std::stoi(timeStrings[2]);
        //Minute:
        currentTime.minute = std::stoi(timeStrings[1]);
        //Hour:
        currentTime.hour = std::stoi(timeStrings[0]);

        return currentTime;
}
inline std::string getCurrTimeStr(){
    timeObj time = getCurrentTime();
    std::string strtime = std::to_string(time.day) + "/" + std::to_string(time.month) + "/" + std::to_string(time.year) + " " +
                          std::to_string(time.hour) + ":" + std::to_string(time.minute) + ":" + std::to_string(time.second);
    return strtime;
}



inline std::string getIP(){
    //Fuck it, I'm too stupid for libcurl. Lets do it like this
    std::string myIP = "";
    //Get ip via console command and save it in ip.txt:
    std::string command = "curl http://api.ipaddress.com/myip?parameters > " + configPath + "ip.txt";
    std::system(command.c_str());

    //Read ip.txt and return its content:
    std::ifstream ifile;
    ifile.open(configPath + "ip.txt");
    if(ifile.is_open()){
        ifile >> myIP;
        ifile.close();
    }
    return myIP;
}
inline bool intToBool(const int val){
    if(val == 0){
        return false;
    }
    return true;
}
