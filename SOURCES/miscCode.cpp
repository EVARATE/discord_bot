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
#include <cstdio>
#include <initializer_list>


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
inline stringVec returnMatches(std::string& str, std::string strReg){
    std::regex reg(strReg);
    return returnMatches(str, reg);
}
inline stringVec strToWords(std::string str){
    std::regex reg("[^ ]+");
    return returnMatches(str, reg);
}
inline void addHelpEntry(std::string& msg, std::string& prefix, const std::string& name, stringVec& triggers){
    msg.append(name + ": ");
    for(auto it = triggers.begin(); it != triggers.end(); ++it){
        msg.append("`" + prefix + *it + "`, ");
    }
    //Delete last characters ', '
    msg.pop_back();
    msg.pop_back();
    msg.append("\\n");
}

inline std::string getCurrTimeStr(){
    //This caused segmentation faults for some reason. Therefor dummy_time

    //time_t now = time(0);
    //tm *ltm = localtime(&now);

    //return std::to_string(ltm->tm_mday) + "/" + std::to_string(1 + ltm->tm_mon) + "/" + std::to_string(1900 + ltm->tm_year).substr(2, 3) + " " +
    //      std::to_string(1 + ltm->tm_hour) + ":" + std::to_string(ltm->tm_min) + ":" + std::to_string(ltm->tm_sec);
    return "dummy_time";
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
inline bool starts_with(const std::string& sample, const std::string& pref){
    if (sample.rfind(pref, 0) == 0) {
      return true;
    }
    return false;
}
inline void findAndReplaceAll(std::string & data, std::string toSearch, std::string replaceStr)
{
    // Get the first occurrence
    size_t pos = data.find(toSearch);

    // Repeat till end is reached
    while( pos != std::string::npos)
    {
        // Replace this occurrence of Sub String
        data.replace(pos, toSearch.size(), replaceStr);
        // Get the next occurrence from the current position
        pos =data.find(toSearch, pos + replaceStr.size());
    }
}
inline std::string findAndReplaceFirst(std::string str, const std::string& from, const std::string& to) {
    size_t start_pos = str.find(from);
    if(start_pos == std::string::npos)
        return str;
    str.replace(start_pos, from.length(), to);
    return str;
}

//===STRUCTS THAT NEED ABOVE FUNCTIONS===

struct Ctrigger{
    std::string identifier;
    stringVec triggers;

    Ctrigger(std::initializer_list<std::string> il): triggers(il) {
        if(il.size() > 0){
            identifier = triggers[0];
        }
    };
    Ctrigger(std::string id, stringVec trgs): identifier(id), triggers(trgs) {};

    std::string operator[](unsigned int index) {return triggers[index];};

    std::string triggerByID(std::string& searchID){
        //See if identifier exists and return it
        //Possible identifiers: '<identifier>', '<identifier><trigger_index>'

        //See if searchID starts with identifier:
        if(!starts_with(searchID, identifier)){return "";}

        //Get trigger_index if exists:
        stringVec indices = returnMatches(searchID, "\\d+");
        if(indices.size() > 0){
            int index = std::stoi(indices[0]);
            //Return trigger at index if exists
            if((int)triggers.size() - 1 >= index){
                return triggers[index];
            }
        }else{
            return  triggers[0];
        }
        return "";
    }
};
