#include "commandclient.h"


//Session actions
void commandClient::onMessage(SleepyDiscord::Message message){
    //Split command into words:
    auto commandLower = toLowerCase(message.content);
    commandLower.erase(0, prefix.size());
    auto command = strToWords(message.content);
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
        //IP
        if(command[0] == trig_ip[0]){
            com_ip(message);
            return;
        }
        //POLL
        if(command[0] == trig_poll[0]){
            com_poll(message);
            return;
        }
        if(command[0] == trig_poll[1]){
            //VOTE
            com_vote(message);
            return;
        }
        if(command[0] == trig_poll[2]){
            //UNVOTE
            com_unvote(message);
            return;
        }
        if(command[0] == trig_poll[3]){
            //POLLADD
            com_pollAdd(message);
            return;
        }
        if(command[0] == trig_poll[4]){
            //POLLREM
            com_pollRem(message);
            return;
        }
        if(command[0] == trig_poll[5]){
            //POLLCLOSE
            com_pollClose(message);
            return;
        }
        if(command[0] == trig_poll[6]){
            //POLLSET
            com_pollSet(message);
            return;
        }
        if(command[0] == trig_quote[0]){
            //QUOTE
            com_quote(message);
            return;
        }

    }
}
void commandClient::onReady(std::string *jsonMessage){
    isConnected = true;
    updateIPInfo();
    static bool firstCall = true;//If 'onReady' is called for the first time
    if(firstCall){
        loadTextCommands();
        loadAllPolls();
        //Update all poll messages:
        for(auto it = polls.begin(); it != polls.end(); ++it){
            updatePollData(it->id);
        }

        updateHelpMsg();
        toLog("---NEW SESSION---");
        firstCall = false;
    }else{
        toLog("---RENEWED SESSION---");
    }

}
void commandClient::onDisconnect(){
    isConnected = false;
    toLog("---DISCONNECTED---");
}
void commandClient::onResume(){
    isConnected = true;
    updateIPInfo();
    toLog("---RECONNECTED---");
    if(offlineLogBuffer.size() != 0){
        std::string msgBuffer = "\\n===OFFLINE LOG START===\\n";
        for(auto it = offlineLogBuffer.begin(); it != offlineLogBuffer.end(); ++it){
            msgBuffer.append(*it);
        }
        msgBuffer.append("===OFFLINE LOG END===");
        toLog(msgBuffer, 1);
        offlineLogBuffer.resize(0);
    }
}
void commandClient::onError(SleepyDiscord::ErrorCode errorCode, const std::string errorMessage){
    toLog("*ERROR: " + errorMessage + "*");
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
    std::string text = "\\n";
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
        sendMessage(message.channelID, "Changed prefix to `" + command[1] + "`");
        toLog("Changed prefix to '" + command[1] + "'");
        updateHelpMsg();
    }
    //Update poll messages:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        updatePollData(it->id);
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
    //Make sure values aren't out of range:
    int ll_maxLength = 19;
    if( ((int)strLimits[0].length() >= ll_maxLength) || ((int)strLimits[1].length() >= ll_maxLength) ){
        sendMessage(message.channelID, "Error: Limits out of range.");
        toLog("Invalid 'random' call. Value out of range");
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
void commandClient::com_ip(SleepyDiscord::Message &message){
    std::string ip = getIP();
    sendMessage(message.channelID, ip);
    toLog("Sent IP info to '" + message.author.username + '\'');
}

void commandClient::com_poll(SleepyDiscord::Message &message)
{
    //Find arguments in quotes:
    std::regex argReg("\".+?\"");
    stringVec args = returnMatches(message.content, argReg);
    if(args.size() == 0){return;}
    //Remove quotes:
    stringVec options;
    for(int i = 0; i < (int)args.size(); ++i){
        args[i].erase(args[i].begin());
        args[i].pop_back();//delete characters '\"'
        args[i].pop_back();
        if(i != 0){
            options.push_back(args[i]);
        }
    }

    //Create poll object
    mo_poll newPoll(args[0], options);
    newPoll.author = message.author.username;
    newPoll.pollChannelID = message.channelID;
    newPoll.id = getPollID();
    polls.push_back(newPoll);

    toLog("Created poll#" + std::to_string(newPoll.id) + ":" + std::to_string(newPoll.options.size()));
    updatePollData(newPoll.id);
    deleteMessage(message.channelID, message.ID);
}
void commandClient::com_vote(SleepyDiscord::Message& message){
    //Get pollID and optionID:
    std::regex idReg("\\d+");
    stringVec strIDs = returnMatches(message.content, idReg);
    if(strIDs.size() < 2){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(strIDs[0]);
    int optionID = std::stoi(strIDs[1]);

    //Apply vote:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            it->voteForOption(optionID, message.author.ID);
            updatePollData(pollID);
        }
    }
    deleteMessage(message.channelID, message.ID);
}
void commandClient::com_unvote(SleepyDiscord::Message& message){
    //Get pollID and optionID:
    std::regex idReg("\\d+");
    stringVec strIDs = returnMatches(message.content, idReg);
    if(strIDs.size() < 2){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(strIDs[0]);
    int optionID = std::stoi(strIDs[1]);

    //Apply vote:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            it->unvoteForOption(optionID, message.author.ID);
            updatePollData(pollID);
        }
    }
    deleteMessage(message.channelID, message.ID);
}
void commandClient::com_pollAdd(SleepyDiscord::Message &message){
    std::regex idReg("\\d+");
    stringVec idStr = returnMatches(message.content, idReg);
    if(idStr.size() == 0){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(idStr[0]);

    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Check if poll accepts new entries:
            if( !(it->allowCustOpt || message.author.username == it->author) ){
                deleteMessage(message.channelID, message.ID);
                return;
            }
            //Find all options to be added:
            std::regex newOptReg("\".+?\"");
            stringVec optStrs = returnMatches(message.content, newOptReg);
            if(optStrs.size() == 0){
                deleteMessage(message.channelID, message.ID);
                return;
            }
            //Add all options to the poll:
            for(auto o_it = optStrs.begin(); o_it != optStrs.end(); ++o_it){
                if(o_it->size() >= 4){
                    o_it->erase(o_it->begin());
                    o_it->pop_back();
                    o_it->pop_back();
                    it->addOption(*o_it);
                }
            }

        }
    }
    deleteMessage(message.channelID, message.ID);
    updatePollData(pollID);
}
void commandClient::com_pollRem(SleepyDiscord::Message &message){
    std::regex idReg("\\d+");
    stringVec idStr = returnMatches(message.content, idReg);
    if(idStr.size() < 2){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(idStr[0]);
    int optionID = std::stoi(idStr[1]);

    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Check if user can remove options:
            if(!(it->author == message.author.username)){
                deleteMessage(message.channelID, message.ID);
                return;
            }

            //Remove options:
            it->removeOption(optionID);
            deleteMessage(message.channelID, message.ID);
            updatePollData(pollID);
            return;

        }
    }
}
void commandClient::com_pollSet(SleepyDiscord::Message &message){
    //Get pollID:
    std::regex idReg("\\d+");
    stringVec idStrs = returnMatches(message.content, idReg);
    if(idStrs.size() == 0){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(idStrs[0]);

    //Get settings:
    std::regex setReg("\\w+");
    stringVec setStrs = returnMatches(message.content, setReg);
    if(setStrs.size() == 0){
        deleteMessage(message.channelID, message.ID);
        return;
    }

    //Get poll with pollID:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Only poll author can change settings:
            if(it->author != message.author.username){return;}

            //Process settings:
            for(auto s_it = setStrs.begin(); s_it != setStrs.end(); ++s_it){
                //Toggle named settings:
                if(*s_it == trig_poll[7]){
                    //CUSTOPT
                    it->allowCustOpt = !it->allowCustOpt;
                }
                else if(*s_it == trig_poll[8]){
                    //MULTI
                    it->allowMultipleChoice = !it->allowMultipleChoice;
                }
            }
        }
    }
    updatePollData(pollID);
    deleteMessage(message.channelID, message.ID);
}
void commandClient::com_pollClose(SleepyDiscord::Message& message){
    //Get pollID:
    std::regex idReg("\\d+");
    stringVec strIDs = returnMatches(message.content, idReg);
    if(strIDs.size() == 0){
        deleteMessage(message.channelID, message.ID);
        return;
    }
    int pollID = std::stoi(strIDs[0]);
    //Find poll with pollID and delete it:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Only poll author can delete it:
            if(it->author != message.author.username){return;}

            it->isClosed = true;
            updatePollData(pollID);



            //DELETE FILE FROM DISK:
            //Read content of poll_list.txt into memory and write it back except for the line to be deleted:
            std::ifstream listFile;
            listFile.open(configPath + "poll_list.txt");
            if(listFile.is_open()){
                stringVec listBuffer;
                std::string currLine;
                while(getline(listFile, currLine)){
                    if(currLine != "poll_" + std::to_string(pollID) + ".txt"){
                        listBuffer.push_back(currLine);
                    }
                }
                listFile.close();
                //Write buffer back:
                std::ofstream ofListFile;
                ofListFile.open(configPath + "poll_list.txt");
                if(ofListFile.is_open()){
                    for(auto buf_it = listBuffer.begin(); buf_it != listBuffer.end(); ++buf_it){
                        ofListFile << *buf_it << "\n";
                    }
                    ofListFile.close();
                }
            }
            //Delete corresponding file:
            std::remove((configPath + "polls/poll_" + std::to_string(pollID) + ".txt").c_str());




            //Delete from memory:
            polls.erase(it);
            break;
        }
    }
    deleteMessage(message.channelID, message.ID);
    toLog("Closed poll#" + std::to_string(pollID));
}
void commandClient::com_quote(SleepyDiscord::Message &message){
    //Example command: /quote "Name" "Super zitat" "Optionaler Kontext"
    stringVec quoted = returnMatches(message.content, "\".+?\"");
    if(quoted.size() < 2 || quoted.size() > 3){
        sendMessage(message.channelID, "Error: Invalid input.");
        return;
    }
    //Save quote to file:
    std::ofstream ofile;
    ofile.open(configPath + "prof_quotes.txt", std::ios::app);
    if(ofile.is_open()){
        std::string quote = "";
        for(auto it = quoted.begin(); it != quoted.end(); ++it){
            it->erase(it->begin());
            it->pop_back();
            it->pop_back();
            quote.append(" \"" + *it + "\"");
        }
        ofile << quote << "\n";
        ofile.close();
    }
    //Send quote to prof-quote channel:
    std::string msg = "**\\nPerson:** " + quoted[0];
    msg.append("\\n**Zitat:** " + quoted[1]);
    if(quoted.size() == 3){
        msg.append("\\n**Kontext:** " + quoted[2]);
    }
    sendMessage("716682386947047455", msg);
    sendMessage(message.channelID, "Saved quote.");
    toLog("Saved new quote");
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

#ifndef Debug

    std::string msg;
    msg.append("**\\nHILFE MENÜ**\\n\\n");
    //Triggers:
    addHelpEntry(msg, prefix, "Regeln", trig_rules);
    addHelpEntry(msg, prefix, "Hilfe", trig_help);
    addHelpEntry(msg, prefix, "Prefix ändern", trig_prefix);
    addHelpEntry(msg, prefix, "Zufällige Zahl zwischen <min> <max>", trig_random);
    msg.append("Zitat speichern: `" + trig_quote[0] + " \\\"<Dozent>\\\" \\\"<Zitat>\\\" \\\"<Optionaler Kontext>\\\"\\n");
    //Textcommands:
    msg.append("Infos zu Vorlesungen:");
    for(auto it = lectureCommands.begin(); it != lectureCommands.end(); ++it){
            msg.append("`" + it->triggers[0] + "`, ");
    }
    //Delete last characters ', '
    msg.pop_back();
    msg.pop_back();

    //Poll:
    msg.append("\\n\\n**Abstimmungen:**\\n");
    msg.append("Neue Abstimmung: `" + prefix + trig_poll[0] + " \\\"<Frage>\\\" \\\"<option1>\\\" \\\"<option2>\\\" ...`\\n");
    msg.append("Abstimmen: `" + prefix + trig_poll[1] + " <pollID> <optionID>`\\n");
    msg.append("Stimme zurücknehmen: `" + prefix + trig_poll[2] + " <pollID> <optionID>`\\n");
    msg.append("Optionen hinzufügen: `" + prefix + trig_poll[3] + " <pollID> \\\"<option1>\\\" \\\"<option2>\\\" ...`\\n");
    msg.append("Option löschen: `" + prefix + trig_poll[4] + " <pollID> <optionID>`\\n");
    msg.append("*Einstellung umschalten: `" + prefix + trig_poll[6] + " <pollID> <setting1> <setting2> ...`\\n");
    msg.append("Abstimmung beenden: `" + prefix + trig_poll[5] + " <pollID>`\\n");

    //Poll settings:
    msg.append("\\n*Einstellungen an - oder ausschalten:\\n");
    msg.append("        `" + trig_poll[7] + "`: Andere können Optionen hinzufügen.\\n");
    msg.append("        `" + trig_poll[8] + "`: Mehrere Antworten auswählbar.\\n");
    msg.append("**Beispiel:** `" + prefix + trig_poll[6] + " 0 " + trig_poll[8] + "`: Multiple Choice umgeschalten.\\n");

    //Update messages:
    help_msg = msg;
    editMessage("702968771735978194", "702969362679857283", msg);
    toLog("Updated help message.");

#endif
}

void commandClient::toLog(const std::string &text, int status){

#ifndef Debug

    std::string time = getCurrTimeStr();

    std::string msg = "[" + time + "]: " + text + "\n";
    std::string discordMsg = "[" + time + "]: " + text + "\\n";

    //Send to log chat:
    if(isConnected){
        sendMessage(logChannelID, discordMsg);
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

#endif
}
void commandClient::updateIPInfo(){
#ifndef Debug
    std::string ip = getIP();
    sendMessage("702765369940639879", "IP: **" + ip + "**");
#endif
}
int commandClient::getPollID(){
    nextPollID++;
    return nextPollID - 1;
}
void commandClient::updatePollData(const int pollID){
    //Get poll:
    for(int i = 0; i < (int)polls.size(); ++i){
        if(polls[i].id == pollID){

            std::string pollMsg = "\\nUmfrage **#" + std::to_string(polls[i].id) + "** von **" + polls[i].author + "**\\n";
            pollMsg.append("```\\n" + polls[i].topic + "\\n```\\n");
            for(auto it = polls[i].options.begin(); it != polls[i].options.end(); ++it){
                pollMsg.append("**" + std::to_string(it->id) + ":** " + it->value + "    **" +
                               std::to_string(polls[i].getOptPercentage(it->id)) + "%** (" +
                               std::to_string(it->voteCount) + "/" + std::to_string(polls[i].totalVotes()) + ")\\n");
            }

            pollMsg.append("\\nMultiple Choice (`" + trig_poll[8] + "`): ");
            if(polls[i].allowMultipleChoice){
                pollMsg.append("Ja.\\n");
            }else{
                pollMsg.append("Nein.\\n");
            }
            pollMsg.append("Eigene Antworten erlaubt (`" + trig_poll[7] + "`): ");
            if(polls[i].allowCustOpt){
                pollMsg.append("Ja.\\n");
            }else{
                pollMsg.append("Nein.\\n");
            }

            if(!polls[i].isClosed){
                pollMsg.append("\\nAuswahl mit `" + prefix + trig_poll[1] + " " + std::to_string(polls[i].id) + " <option_ID>`\\n");
                pollMsg.append("Einstellungen ändern mit `" + prefix + trig_poll[6] + " " + std::to_string(polls[i].id) + " <setting1> <setting2> ...`");
            }else{
                pollMsg.append("\\nUmfrage wurde geschlossen.");
            }
            if(!polls[i].messageExists){
                auto newMessage = sendMessage(polls[i].pollChannelID, pollMsg);
                polls[i].pollMessageID = newMessage.cast().ID;
                polls[i].messageExists = true;
            }else{
                editMessage(polls[i].pollChannelID, polls[i].pollMessageID, pollMsg);
            }

            //Save poll to disk:
            savePoll(polls[i]);

            //Logmessage:
            std::string logMsg = "Updated poll#" + std::to_string(polls[i].id);
            for(auto it = polls[i].options.begin(); it != polls[i].options.end(); ++it){
                logMsg.append("-" + std::to_string(it->voteCount));
            }
            toLog(logMsg);

        }
    }

}
void commandClient::loadAllPolls(){

    //Get filepaths to all polls:
    stringVec paths;
    std::ifstream listFile;
    listFile.open(configPath + "poll_list.txt");
    if(!listFile.is_open()){return;}
    do{
        std::string currPath;
        listFile >> currPath;
        if(currPath.size() > 0){
            paths.push_back(currPath);
        }
    }while(!listFile.eof());
    listFile.close();
    if(paths.size() == 0){return;}

    //Load all files:
    for(auto it = paths.begin(); it != paths.end(); ++it){
        if(it->size() > 0){
            //Create mo_poll object, load it and save it in commandClient
            mo_poll currPoll(configPath + "polls/" + *it);
            currPoll.id = getPollID();
            polls.push_back(currPoll);
        }
    }
    toLog("Loaded " + std::to_string(paths.size()) + " polls from disk.");

}
void commandClient::savePoll(mo_poll& poll){

    std::string saveName = "poll_" + std::to_string(poll.id) + ".txt";

    //See if entry already exists:
    std::ifstream ifile;
    ifile.open(configPath + "poll_list.txt");
    if(ifile.is_open()){
        std::string currLine;
        while(getline(ifile, currLine)){
            if(currLine == saveName){
                //Save poll to file in subdirectory:
                poll.savePoll(configPath + "polls/" + saveName);
                return;
            }
        }
        ifile.close();
    }
    //Add entry in overall poll list:
    std::ofstream listFile;
    listFile.open(configPath + "poll_list.txt", std::ios::app);
    if(!listFile.is_open()){return;}
    listFile << saveName << "\n";
    listFile.close();
    poll.isSaved = true;

    //Save poll to file in subdirectory:
    poll.savePoll(configPath + "polls/" + saveName);

}
