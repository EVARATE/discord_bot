#include "myclientclass.h"



//Access:
SleepyDiscord::Channel MyClientClass::channelByName(std::string channelName){
    auto channelCache = getServerChannels(serverID);
    for(int i = 0; i < (int)channelCache.vector().size(); ++i){
        if(channelCache.vector()[i].name == channelName){
            return channelCache.vector()[i];
        }
    }
    return SleepyDiscord::Channel();
}
SleepyDiscord::User MyClientClass::userByName(std::string userName){
    auto userList = listMembers(serverID, 1000);
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userList.vector()[i].user.username == userName){
            return userList.vector()[i].user;
        }
    }
    return SleepyDiscord::User();//Else return empty user
}
SleepyDiscord::User MyClientClass::userByNick(std::string userNick){
    auto userList = listMembers(serverID, 1000);
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userList.vector()[i].nick == userNick){
            return userList.vector()[i].user;
        }
    }
    return SleepyDiscord::User();//Else return empty user
}
std::vector<SleepyDiscord::User> MyClientClass::usersInChannel(std::string channelID){
    return getChannel(channelID).cast().recipients;
}
std::vector<SleepyDiscord::User> MyClientClass::usersWithRole(std::string roleName){
    auto userList = listMembers(serverID, 1000);
    std::vector<SleepyDiscord::User> users;
    for(int i = 0; i < (int)userList.vector().size(); ++i){
        if(userHasRole(userList.vector()[i].user.ID, roleName)){
            users.push_back(userList.vector()[i]);
        }
    }
    return users;
}
bool MyClientClass::userHasRole(std::string userID, std::string roleName){
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
std::string MyClientClass::getRuleMsg(){
    SleepyDiscord::Channel ruleChannel = channelByName("regeln");
    SleepyDiscord::Message ruleMessage = getMessage(ruleChannel.ID, ruleMessageID);
    return ruleMessage.content;
}

//Other
void MyClientClass::addLecture(const std::string& name,
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

//Actions:
void MyClientClass::toConsoleLog(const std::string &text){
    auto rawTime = std::chrono::system_clock::now();
    std::time_t currTime = std::chrono::system_clock::to_time_t(rawTime);
    std::string time = std::ctime(&currTime);

    //Only print time and date
    std::regex timeReg("[^ ]+");
    stringVec timeData = returnMatches(time, timeReg);
    stringVec months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
    std::string month;
    for(int i = 0; i < (int)months.size(); ++i){
        if(months[i] == timeData[1]){
            month = std::to_string(i + 1);
            break;
        }
    }
    std::string year = timeData[4].substr(2,3);
    std::string strtime = timeData[2] + "/" + month + "/" + year + " " + timeData[3];

    strtime.erase(std::remove(strtime.begin(), strtime.end(), '\n'), strtime.end());

    std::string msg = "[" + strtime + "]: " + text + '\n';
    //Console output:
    fprintf(stderr, msg.c_str());
    //Write to logfile:
    std::ofstream ofile;
    ofile.open("discord_log.txt",std::ios::app);
    if(ofile.is_open()){
        ofile << msg;
        ofile.close();
    }
}
void MyClientClass::setupData(){
    //Vorlesungen:
    addLecture("e4",
               "Montag, 12:00 - 14:00 Uhr",
               "Mittwoch, 12:00 - 14:00 Uhr",
               "kein Eintrag",
               "kein Eintrag",
               "*Montag:* [ID: 966 2727 0626 | PW: 446925] *Mittwoch:* [ID: 977 7420 6032 | PW: 555418]"
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
               "Daten ändern sich ständig"
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
               "weis ich nich"
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
void MyClientClass::updateHelpMsg(){
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
void MyClientClass::backgroundWork(){
    int counter = 0;
    while(true){
        editMessage(channelByName("bot-infos").ID, "705449791769018450", std::to_string(counter));
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

}

//Commands
void MyClientClass::sendRulesMsg(SleepyDiscord::Message message){
    sendMessage(message.channelID, getRuleMsg());
    toConsoleLog("Printed rule-message");
}
void MyClientClass::sendHelpMsg(SleepyDiscord::Message message){
    sendMessage(message.channelID, helpMessage);
    toConsoleLog("Printed help-message");
}
void MyClientClass::setPrefix(std::string newPrefix){
    if(prefix.length() > 0){
        prefix = newPrefix;
        toConsoleLog("Changed prefix to '" + newPrefix + "'");
    }

}
void MyClientClass::sendRandom(SleepyDiscord::Message message, std::string rawOptions){
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
void MyClientClass::sendLectureInfo(SleepyDiscord::Message message, std::string name){
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

void MyClientClass::onMessage(SleepyDiscord::Message message){
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
