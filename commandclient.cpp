#include "commandclient.h"

//Access:
SleepyDiscord::Channel commandClient::channelByName(std::string channelName){
    auto channelCache = getServerChannels(serverID);
    for(int i = 0; i < (int)channelCache.vector().size(); ++i){
        if(channelCache.vector()[i].name == channelName){
            return channelCache.vector()[i];
        }
    }
    return SleepyDiscord::Channel();
}
SleepyDiscord::User commandClient::userByName(std::string userName){
    auto userList = listMembers(serverID, 1000);
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userList.vector()[i].user.username == userName){
            return userList.vector()[i].user;
        }
    }
    return SleepyDiscord::User();//Else return empty user
}
SleepyDiscord::User commandClient::userByNick(std::string userNick){
    auto userList = listMembers(serverID, 1000);
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userList.vector()[i].nick == userNick){
            return userList.vector()[i].user;
        }
    }
    return SleepyDiscord::User();//Else return empty user
}
std::vector<SleepyDiscord::User> commandClient::usersInChannel(std::string channelID){
    return getChannel(channelID).cast().recipients;
}
std::vector<SleepyDiscord::User> commandClient::usersWithRole(std::string roleName){
    auto userList = listMembers(serverID, 1000);
    std::vector<SleepyDiscord::User> users;
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userHasRole(userList.vector()[i].user.ID, roleName)){
            users.push_back(userList.vector()[i]);
        }
    }
    return users;
}
bool commandClient::userHasRole(std::string userID, std::string roleName){
    auto user = getUser(userID);
    auto userList = listMembers(serverID, 1000);
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userList.vector()[i].user.ID == user.cast().ID){
            //See if user has role:
            auto &userRoles = userList.vector()[i].roles;
            for(int j = 0; j < (int)userRoles.size(); ++j){
                if(userRoles[j].string() == roleName){
                    return true;
                }
            }
        }
    }
    return false;
}
std::string commandClient::getRuleMsg(){
    SleepyDiscord::Channel ruleChannel = channelByName("regeln");
    SleepyDiscord::Message ruleMessage = getMessage(ruleChannel.ID, ruleMessageID);
    return ruleMessage.content;
}

//Other
void commandClient::addLecture(const std::string& name,
                               const std::string& termin1,
                               const std::string& termin2,
                               const std::string& klausur,
                               const std::string& nachklausur,
                               const std::string& zoomDaten){
    vorlesung vl;
    vl.name = name;
    vl.termin1 = termin1;
    vl.termin2 = termin2;
    vl.klausur = klausur;
    vl.nachklausur = nachklausur;
    vl.zoomDaten = zoomDaten;
    vorlesungen.push_back(vl);
}

void toLowerCase(std::string &str){
    std::transform(str.begin(), str.end(), str.begin(),
        [](unsigned char c){ return std::tolower(c); });
}
void removeSpaces(std::string &str){
    std::string::iterator end_pos = std::remove(str.begin(), str.end(), ' ');
    str.erase(end_pos, str.end());
}
bool stringContains(const std::string & text, const std::string & subtext){
    if (text.find(subtext) != std::string::npos) {
        return true;
    }else{
        return false;
    }
}
bool stringContains(const std::string & text, const char & subtext){
    if (text.find(subtext) != std::string::npos) {
        return true;
    }else{
        return false;
    }
}
template <typename T>
bool vecContains(T element, std::vector<T> vec){
    typename std::vector<T>::iterator it;
    for(it = vec.begin(); it != vec.end(); ++it){
        if(*it == element){
            return true;
        }
    }
    return false;
}
stringVec returnMatches(std::string str, std::regex reg){
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
bool strContainsRegex(const std::string& str, std::string regStr){
    std::regex reg(regStr);
    stringVec matches = returnMatches(str, reg);
    if(matches.size() > 0){
        return true;
    }else{
        return false;
    }
}

//Actions:
void commandClient::toConsoleLog(const std::string &text){

    timeObj time = getCurrentTime();
    std::string strtime = std::to_string(time.day) + "/" + std::to_string(time.month) + "/" + std::to_string(time.year) + " " +
                          std::to_string(time.hour) + ":" + std::to_string(time.minute) + ":" + std::to_string(time.second);

    std::string msg = "[" + strtime + "]: " + text + '\n';
    //Console output:
    fprintf(stderr, msg.c_str());
    //To log chat:
    sendMessage("712643802996932648", msg);
    //Write to logfile:
    std::ofstream ofile;
    ofile.open("discord_log.txt",std::ios::app);
    if(ofile.is_open()){
        ofile << msg;
        ofile.close();
    }
}
void commandClient::setupData(){
    //Vorlesungen:
    addLecture("e4",
               "Montag, 12:00 - 14:00 Uhr",
               "Mittwoch, 12:00 - 14:00 Uhr",
               "kein Eintrag",
               "kein Eintrag",
               "977 7420 6032 | 555418"
                );
    addLecture("e2",
               "Montag, 0:15 - 10:00 Uhr",
               "Freitag, 8:15 - 10:00 Uhr",
               "Wärme: 08.06.20, 8:15 - 9:45 Uhr; A240, B201, N120 \\n      Elektro: 30.07.20, 9:15 - 10:45 Uhr; N120, B101, B201",
               "23.09.20, 9:15 - 10:45 Uhr; H030",
               "unbekannt"
                );
    addLecture("m4",
               "Montag, 10:00 - 12:00 Uhr",
               "Donnerstag, 8:00 - 10:00 Uhr",
               "06.08.20, 08:00 - 10:30 Uhr; N120, B201",
               "unbekannt",
               "Mo: `992 2654 3328 | nUmA20m4`, Do: `936 5948 3067 | A0fG%do`, ZÜ: `918 1344 4557 | h5Vdf&k`"
                );
    addLecture("m2",
               "unbekannt, bitte Vorlesungsseite an Mo schicken",
               "unbekannt",
               "unbekannt",
               "unbekannt",
               "unbekannt"
                );
    addLecture("t3",
               "Dienstag, 8:00 - 10:00 Uhr",
               "Donnerstag, 14:00 - 16:00 Uhr",
               "unbekannt",
               "unbekannt",
               "VL: `995 3333 4815 | 444026` ZÜ: `97221197555 | 622587"
                );
    addLecture("t1",
               "Montag, 10:00 - 12:00 Uhr",
               "Mittwoch, 10:00 - 12:00 Uhr",
               "unbekannt",
               "unbekannt",
               "Keine."
                );



    toConsoleLog("\n\
+--------------------+\n\
|Starting Discord Bot|\n\
+--------------------+\n");

                 //Setup helpMessage:
                 updateHelpMsg();

}
void commandClient::updateHelpMsg(){
    helpMessage = "**\\nHILFE MENÜ**\\n\\n\
*Regeln:* `" + prefix + "rules`, `" + prefix + "regeln`\\n\
*Hilfe:* `" + prefix + "help`, `" + prefix + "hilfe`\\n\
*Zufällige Zahl zwischen* **min** *und* **max**: `" + prefix + "random <min>:<max>`\\n\
*Prefix ändern:* `" + prefix + "setprefix <prefix>`\\n\
*Infos zu Vorlesungen:* ";
    for(int i = 0; i < (int)vorlesungen.size(); ++i){
        std::string str = "`" + prefix + vorlesungen[i].name + "`, ";
        helpMessage.append(str);
    }
    //Update bot infos
    editMessage(channelByName("bot-infos").ID, helpMessageID, helpMessage);
    toConsoleLog("Updated help message");
}
timeObj commandClient::getCurrentTime(){
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



//Commands
void commandClient::sendRulesMsg(SleepyDiscord::Message message){
    sendMessage(message.channelID, getRuleMsg());
    toConsoleLog("Printed rule-message");
}
void commandClient::sendHelpMsg(SleepyDiscord::Message message){
    sendMessage(message.channelID, helpMessage);
    toConsoleLog("Printed help-message");
}
void commandClient::setPrefix(std::string newPrefix){
    if(prefix.length() > 0){
        prefix = newPrefix;
        updateHelpMsg();
        toConsoleLog("Changed prefix to '" + newPrefix + "'");
    }

}
void commandClient::sendRandom(SleepyDiscord::Message message, std::string rawOptions){
    std::regex numReg("\\d+");
    stringVec limits = returnMatches(rawOptions, numReg);
    if(limits.size() < 2){
        sendMessage(message.channelID, "ERROR: Invalid input");
        toConsoleLog("Invalid 'random' options: " + rawOptions);
        return;
    }
    std::string smin = limits[0];
    std::string smax = limits[1];

    int val1 = std::abs(std::stoi(smin));
    int val2 = std::abs(std::stoi(smax));
    static std::mt19937_64 generator(time(0));
    std::uniform_int_distribution<int> distribution(std::min(val1, val2), std::max(val1, val2));
    auto rNumber = distribution(generator);
    sendMessage(message.channelID, "**" + std::to_string(rNumber) + "**");
    toConsoleLog("Generated random number: " + std::to_string(rNumber));
}
void commandClient::sendLectureInfo(SleepyDiscord::Message message, std::string name){
    for(int i = 0; i < (int)vorlesungen.size(); ++i){
        if(vorlesungen[i].name == name){
            sendMessage(message.channelID, "**\\nName:** " + vorlesungen[i].name + "\\n" +
                                           "**Vorlesung 1:** " + vorlesungen[i].termin1 + "\\n" +
                                           "**Vorlesung 2:** " + vorlesungen[i].termin2 + "\\n" +
                                           "**Klausur:** " + vorlesungen[i].klausur + "\\n" +
                                           "**Nachklausur:** " + vorlesungen[i].nachklausur + "\\n" +
                                           "**Zoom Daten:** " + vorlesungen[i].zoomDaten
                        );
            toConsoleLog("Printed lecture info: '" + name + "'");
            break;
        }
    }
}
void commandClient::sendDirMessage(const std::string &userName, const std::string &text){
    auto user = userByName(userName);
    auto dirChannel = createDirectMessageChannel(user.ID);
    std::string dirChannelID = dirChannel.cast().ID;
    sendMessage(dirChannelID, text);
}



void commandClient::onMessage(SleepyDiscord::Message message){
    //Look for commands:
    if(message.startsWith(prefix)){
        //Split command into command and options
        toLowerCase(message.content);
        std::regex comReg("[^ ]+");
        stringVec command = returnMatches(message.content, comReg);
        //Remove prefix:
        std::string newCom;
        for(int i = prefix.size(); i < (int)command[0].size(); ++i){
            newCom.push_back(command[0][i]);
        }
        command[0] = newCom;

        //Possible commands:
        stringVec helpList = {"hilfe", "help"};
        stringVec ruleList = {"regeln", "rules"};
        stringVec randList = {"random"};
        stringVec prefixList = {"setprefix"};
        stringVec lectureList;
        for(int i = 0; i < (int)vorlesungen.size(); ++i){
            lectureList.push_back(vorlesungen[i].name);
        }

        //HELP
        if(vecContains(command[0], helpList)){
            sendHelpMsg(message);
            return;
        }

        //RULES
        if(vecContains(command[0], ruleList)){
            sendRulesMsg(message);
            return;
        }

        //RANDOM
        if(vecContains(command[0], randList)){
            if(command.size() >= 2){
                sendRandom(message, command[1]);
            }
            return;
        }

        //PREFIX
        if(vecContains(command[0], prefixList)){
            if(command.size() >= 2){
                setPrefix(command[1]);
            }
            return;
        }

        //LECTURE INFO
        if(vecContains(command[0], lectureList)){
            sendLectureInfo(message, command[0]);
            return;
        }




    }
}
void commandClient::onError(SleepyDiscord::ErrorCode errorCode, const std::string errorMessage){
    if(errorMessage == "Unknown"){return;}
    toConsoleLog(errorMessage);
}
