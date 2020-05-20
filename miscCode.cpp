#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <regex>
#include <stdlib.h>


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
    stringVec commands;//Multiple commands can trigger this
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
inline stringVec toWords(std::string str){
    std::regex reg("[^ ]+");
    return returnMatches(str, reg);
}
