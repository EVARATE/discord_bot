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
        //Check for text commands:
        execTextCommand(command, message);
    }
}
void commandClient::onReady(std::string *jsonMessage){
    isConnected = true;
    loadTextCommands();
}
void commandClient::onDisconnect(){
    isConnected = false;
}
void commandClient::onResume(){
    isConnected = true;
}

//Commands
void commandClient::execTextCommand(stringVec &command, SleepyDiscord::Message &message){
    //Cycle through all text commands and see if one fits:
    for(auto it = textCommands.begin(); it != textCommands.end(); ++it){
        for(auto cit = it->commands.begin(); cit != it->commands.end(); ++cit){
            if(*cit == command[0]){
                respondTextCommand(*it, message.channelID);
                return;
            }
        }
    }
}
void commandClient::respondTextCommand(textCommand &command, const std::string& channelID){
    std::string text;
    for(auto it = command.properties.begin(); it != command.properties.end(); ++it){
        text.append("**" + it->name + "** " + it->value + "\\n");
    }
    sendMessage(channelID, text);
    toLog("Responded to equivalent of '" + command.commands[0] + '\'');
}

//Other
void commandClient::loadTextCommands(){
    std::ifstream ifile;
    ifile.open(configPath + "textCommands.txt");
    if(!ifile.is_open()){
        fprintf(stderr, "Couldn't open 'textCommands.txt'");
        return;
    }
    textCommands.resize(0);
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
            currCommand.commands = commands;
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
            textCommands.push_back(currCommand);
        }
    }
    toLog("Loaded text commands.");
}
void commandClient::toLog(const std::string &text){
    std::string time = "[DUMMY TIME]"; //Placeholder for time==================TO DO===========================

    std::string msg = time + ": " + text + "\n";
    std::string discordMsg = time + ": " + text + "\\n";

    //Send to log chat:
    if(isConnected){
        //sendMessage("712643802996932648", discordMsg);
    }else{
        offlineLogBuffer.push_back(discordMsg);
    }

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
