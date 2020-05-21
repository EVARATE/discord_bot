#include "commandclient.h"


//Session actions
void commandClient::onMessage(SleepyDiscord::Message message){
    //Split command into words:
    auto commandLower = toLowerCase(message.content);
    commandLower.erase(0, prefix.size());
    auto command = toWords(message.content);
    command[0].erase(0, prefix.size());

    //Look for commands:
    if(message.startsWith(prefix)){
        //Check for text commands (if any are called)
        execTextCommand(command, message);

        //RULES
        if(command[0] == trig_rules[0] ||
           command[0] == trig_rules[1]){
            com_rules(message);
            return;
        }
        //HELP
        if(command[0] == trig_help[0] ||
           command[0] == trig_help[1]){
            com_help(message);
            return;
        }
        //PREFIX
        if(command[0] == trig_prefix[0]){
            com_prefix(message);
            return;
        }
        //RANDOM
        if(command[0] == trig_random[0]){
            com_random(message);
            return;
        }
        //RELOAD COMMANDS
        if(command[0] == trig_relComs[0]){
            com_reloadCommands();
            return;
        }
        //LOG
        if(command[0] == trig_log[0]){
            com_log(message);
            return;
        }

    }
}
void commandClient::onReady(std::string *jsonMessage){
    isConnected = true;
    static bool firstCall = true;//If 'onReady' is called for the first time
    if(firstCall){
        loadTextCommands();
        updateHelpMsg();
        firstCall = false;
    }
}
void commandClient::onDisconnect(){
    isConnected = false;
}
void commandClient::onResume(){
    isConnected = true;
    if(offlineLogBuffer.size() != 0){
        std::string msgBuffer = "===OFFLINE LOG START===\\n";
        for(auto it = offlineLogBuffer.begin(); it != offlineLogBuffer.end(); ++it){
            msgBuffer.append(*it + "\n");
        }
        msgBuffer.append("===OFFLINE LOG END===");
        toLog(msgBuffer, 1);
        offlineLogBuffer.resize(0);
    }
}

//Commands
void commandClient::execTextCommand(stringVec &command, SleepyDiscord::Message &message){
    //Cycle through all text commands and see if one fits:
    for(auto it = lectureCommands.begin(); it != lectureCommands.end(); ++it){
        for(auto cit = it->triggers.begin(); cit != it->triggers.end(); ++cit){
            if(*cit == command[0]){
                respondTextCommand(*it, message.channelID);
                return;
            }
        }
    }
}
void commandClient::respondTextCommand(textCommand &command, const std::string& channelID){
    std::string text = "**\\n**";
    for(auto it = command.properties.begin(); it != command.properties.end(); ++it){
        text.append("**" + it->name + "** " + it->value + "\\n");
    }
    sendMessage(channelID, text);
    toLog("Responded to '" + command.triggers[0] + '\'');
}
void commandClient::com_rules(SleepyDiscord::Message &message){
    //Read message:
    SleepyDiscord::Message ruleMessage = getMessage(ruleChannelID, ruleMessageID);
    //Send rules:
    sendMessage(message.channelID, ruleMessage.content);
    //Log:
    toLog("Sent rule message.");
}

void commandClient::com_help(SleepyDiscord::Message &message)
{
    sendMessage(message.channelID, help_msg);
    toLog("Sent help message.");
}

void commandClient::com_prefix(SleepyDiscord::Message &message)
{
    std::regex reg("[^ ]+");
    auto command = returnMatches(message.content, reg);
    if(command.size() >= 2){
        prefix = command[1];
        toLog("Changed prefix to '" + command[1] + "'");
        updateHelpMsg();
    }
}

void commandClient::com_random(SleepyDiscord::Message &message)
{
    //Get numbers from command:
    std::regex numReg("\\d+");
    stringVec strLimits = returnMatches(message.content, numReg);
    if(strLimits.size() < 2){
        sendMessage(message.channelID, "Error: Invalid input");
        toLog("Invalid 'random' call");
        return;
    }
    //To long long:
    std::string strMin = strLimits[0];
    std::string strMax = strLimits[1];
    long long val1 = std::abs(std::stoll(strMin));
    long long val2 = std::abs(std::stoll(strMax));
    //Generate number:
    static std::mt19937_64 generator;
    std::uniform_int_distribution<long long> distribution(std::min(val1, val2), std::max(val1, val2));
    auto rNumber = distribution(generator);
    sendMessage(message.channelID, "**" + std::to_string(rNumber) + "**");
    toLog("Generated Random number: " + std::to_string(rNumber));
}

void commandClient::com_reloadCommands()
{
    loadTextCommands();
}
void commandClient::com_log(SleepyDiscord::Message &message){
    std::regex reg("[^ ]+");
    stringVec command = returnMatches(message.content, reg);
    if(command.size() >= 2){
        std::string msg = message.content;
        msg.erase(0, command[0].size() + 1);
        toLog(msg);
        sendMessage(message.channelID, "Logged message.");
    }else{
        sendMessage(message.channelID, "Invalid input.");
    }
}

//Other
void commandClient::loadTextCommands(){
    std::ifstream ifile;
    ifile.open(configPath + "textCommands.txt");
    if(!ifile.is_open()){
        fprintf(stderr, "Couldn't open 'textCommands.txt'");
        return;
    }
    lectureCommands.resize(0);
    while(!ifile.eof()){
        std::string line;
        getline(ifile, line);
        std::string currLine = toLowerCase(line);

        if(currLine[0] == 'c'){
            //current line is a command
            //Find commands:
            std::regex comReg("'(.*?)'");
            stringVec commands = returnMatches(currLine, comReg);
            //Remove quotes:
            for(auto it = commands.begin(); it != commands.end(); ++it){
                it->erase(it->begin());
                it->pop_back();
            }
            //Create textcommand object:
            textCommand currCommand;
            currCommand.triggers = commands;
            //Read all properties
            bool commOver = false;
            do{
                std::string pLine;
                getline(ifile, pLine);
                if(pLine[0] == 'p'){
                    std::regex comReg("'(.*?)'");
                    stringVec props = returnMatches(pLine, comReg);
                    for(auto it = props.begin(); it != props.end(); ++it){
                        it->erase(it->begin());
                        it->pop_back();
                    }
                    property newProp;
                    newProp.name = props[0];
                    newProp.value = props[1];
                    currCommand.properties.push_back(newProp);
                }else{
                    commOver = true;
                }
            }while(!commOver || ifile.eof());
            lectureCommands.push_back(currCommand);
        }
    }
    toLog("Loaded text commands.");
}
void commandClient::updateHelpMsg(){
    std::string msg;
    msg.append("**\\nHILFE MENÜ**\\n\\n");
    //Triggers:
    addHelpEntry(msg, prefix, "Regeln", trig_rules);
    addHelpEntry(msg, prefix, "Hilfe", trig_help);
    addHelpEntry(msg, prefix, "Prefix ändern", trig_prefix);
    addHelpEntry(msg, prefix, "Zufällige Zahl zwischen <min>:<max>", trig_random);
    //Textcommands:
    msg.append("Infos zu Vorlesungen: ");
    for(auto it = lectureCommands.begin(); it != lectureCommands.end(); ++it){
            msg.append("`" + it->triggers[0] + "`, ");
    }
    //Delete last characters ', '
    msg.pop_back();
    msg.pop_back();

    //Save new message:
    help_msg = msg;
    toLog("Updated help message.");
}

void commandClient::toLog(const std::string &text, int status){
    std::string time = "[DUMMY TIME]"; //Placeholder for time==================TO DO===========================

    std::string msg = time + ": " + text + "\n";
    std::string discordMsg = "*" + time + ": " + text + "*\\n";

    //Send to log chat:
    if(isConnected){
        //sendMessage(logChannelID, discordMsg);
    }else{
        offlineLogBuffer.push_back(discordMsg);
    }

    if(status != 1){
        //Write to console:
        fprintf(stderr, msg.c_str());

        //Write to log file:
        std::ofstream ofile;
        ofile.open(configPath + "log.txt", std::ios::app);
        if(ofile.is_open()){
            ofile << msg;
            ofile.close();
        }else{
            fprintf(stderr, "Couldn't open 'log.txt'");
        }
    }
}
