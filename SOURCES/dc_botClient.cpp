#include "../HEADERS/dc_botClient.h"


//Session actions
void dc_botClient::preInit(ev_log &log)
{
    evLog = log;
#ifndef NDEBUG
    //If cmake is in debug mode
    evLog.log("===INIT DEBUG SESSION===", ev_log::Level::DEBUG);
    evLog.log("Note: prefix is 't/'", ev_log::Level::DEBUG);
    prefix = "t/";
#else
    evLog.log("=== INIT NEW SESSION===");
    prefix = "/";
#endif
    checkExpiredPolls();
    loadTextCommands();
    loadAllPolls();
}

void dc_botClient::onMessage(SleepyDiscord::Message message){
    //Split command into words:
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
        if(command[0] == trig_updHelp[0]){
            //UPDHELP
            com_updhelp(message);
            return;
        }
        if(command[0] == trig_getlog[0]){
            //GETLOG
            com_getLog(message);
            return;
        }

    }
}
void dc_botClient::onReady(SleepyDiscord::Ready readyData){
    static bool firstCall = true;
    if(firstCall){
        firstCall = false;
        //Update all poll messages:
        for(auto& poll : polls){updatePollData(poll.id);}
        updateHelpMsg();
        evLog.log("===CONNECTED SESSION: '" + readyData.sessionID + "' ===");
    }
    else{
        evLog.log("===RECONNECTED SESSION: '" + readyData.sessionID + "' ===");
    }

}
void dc_botClient::onDisconnect(){
    evLog.log("===DISCONNECTED===", ev_log::Level::WARNING);
}

void dc_botClient::onError(SleepyDiscord::ErrorCode errorCode, const std::string errorMessage){
    int code = static_cast<int>(errorCode);
    evLog.log("[" + std::to_string(code) + "] " + errorMessage, ev_log::Level::SLEEPY_ERROR);
}

//Commands
void dc_botClient::execTextCommand(stringVec &command, SleepyDiscord::Message &message){
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
void dc_botClient::respondTextCommand(textCommand &command, const std::string& channelID){
    std::string text = "\n";
    for(auto it = command.properties.begin(); it != command.properties.end(); ++it){
        text.append("**" + it->name + "** " + it->value + "\n");
    }
    sendMessage(channelID, text);
    evLog.log("Responded to '" + command.triggers[0] + '\'');
}
void dc_botClient::com_rules(SleepyDiscord::Message &message){
    //Read message:
    SleepyDiscord::Message ruleMessage = getMessage(ruleChannelID, ruleMessageID);
    //Send rules:
    sendMessage(message.channelID, ruleMessage.content);
    //Log:
    evLog.log("Sent rule message.");
}

void dc_botClient::com_help(SleepyDiscord::Message &message)
{
    sendMessage(message.channelID, help_msg);
    evLog.log("Sent help message.");
}

void dc_botClient::com_prefix(SleepyDiscord::Message &message)
{
    auto command = regex_FindAll(message.content, "[^ ]+");
    if(command.size() >= 2){
        prefix = command[1];
        sendMessage(message.channelID, "Changed prefix to `" + command[1] + "`");
        evLog.log("Changed prefix to '" + command[1] + "'");
        updateHelpMsg();
    }
    //Update poll messages:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        updatePollData(it->id);
    }
}

void dc_botClient::com_random(SleepyDiscord::Message &message)
{
    //Get numbers from command:
    stringVec strLimits = regex_FindAll(message.content, "\\d+");
    if(strLimits.size() < 2){
        sendMessage(message.channelID, "Error: Invalid input");
        return;
    }
    //Make sure values aren't out of range:
    int ll_maxLength = 19;
    if( ((int)strLimits[0].length() >= ll_maxLength) || ((int)strLimits[1].length() >= ll_maxLength) ){
        sendMessage(message.channelID, "Error: Limits out of range.");
        return;
    }
    //To long long:
    std::string strMin = strLimits[0];
    std::string strMax = strLimits[1];
    long long val1 = std::abs(std::stoll(strMin));
    long long val2 = std::abs(std::stoll(strMax));
    //Generate number:
    static std::mt19937_64 generator(static_cast<long unsigned int>(time(0)));
    std::uniform_int_distribution<long long> distribution(std::min(val1, val2), std::max(val1, val2));
    auto rNumber = distribution(generator);
    sendMessage(message.channelID, "**" + std::to_string(rNumber) + "**");
    evLog.log("Generated Random number: " + std::to_string(rNumber));
}

void dc_botClient::com_reloadCommands()
{
    loadTextCommands();
}
void dc_botClient::com_log(SleepyDiscord::Message &message){
    stringVec command = regex_FindAll(message.content, "[^ ]+");
    if(command.size() >= 2){
        std::string msg = message.content;
        msg.erase(0, command[0].size() + 1);
        evLog.log(msg);
        sendMessage(message.channelID, "Logged message.");
    }else{
        sendMessage(message.channelID, "Invalid input.");
    }
}
void dc_botClient::com_ip(SleepyDiscord::Message &message){
    std::string ip = getIP();
    sendMessage(message.channelID, ip);
    evLog.log("Sent bot_server IP info to '" + message.author.username + '\'');
}

void dc_botClient::com_poll(SleepyDiscord::Message &message)
{
    //Find arguments in quotes:
    stringVec args = regex_FindAll(message.content, "\".+?\"");
    if(args.size() == 0){return;}
    //Remove quotes:
    stringVec options;
    for(int i = 0; i < (int)args.size(); ++i){
        args[i].erase(args[i].begin());
        args[i].pop_back();//delete characters '\"'
        if(i != 0){
            options.push_back(args[i]);
        }
    }

    //Create poll object
    mo_poll newPoll(args[0], options);
    newPoll.author = message.author.username;
    newPoll.pollChannelID = message.channelID;
    newPoll.expiryTime = time(0) + 1209600; //Expires in 2 weeks
    newPoll.id = getPollID();
    polls.push_back(newPoll);

    evLog.log("Created poll#" + std::to_string(newPoll.id) + ":" + std::to_string(newPoll.options.size()));
    updatePollData(newPoll.id);
    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
}
void dc_botClient::com_vote(SleepyDiscord::Message& message){
    //Get pollID and optionID:
    stringVec strIDs = regex_FindAll(message.content, "\\d+");
    if(strIDs.size() < 2){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
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
    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
}
void dc_botClient::com_unvote(SleepyDiscord::Message& message){
    //Get pollID and optionID:
    stringVec strIDs = regex_FindAll(message.content, "\\d+");
    if(strIDs.size() < 2){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
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
    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
}
void dc_botClient::com_pollAdd(SleepyDiscord::Message &message){
    stringVec idStr = regex_FindAll(message.content, "\\d+");
    if(idStr.size() == 0){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
        return;
    }
    int pollID = std::stoi(idStr[0]);

    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Check if poll accepts new entries:
            if( !(it->allowCustOpt || message.author.username == it->author) ){
                try {
                    deleteMessage(message.channelID, message.ID);
                } catch (...) {
                    //Already logged through onError()
                }
                return;
            }
            //Find all options to be added:
            stringVec optStrs = regex_FindAll(message.content, "\".+?\"");
            if(optStrs.size() == 0){
                try {
                    deleteMessage(message.channelID, message.ID);
                } catch (...) {
                    //Already logged through onError()
                }
                return;
            }
            //Add all options to the poll:
            for(auto o_it = optStrs.begin(); o_it != optStrs.end(); ++o_it){
                if(o_it->size() >= 4){
                    o_it->erase(o_it->begin());
                    o_it->pop_back();
                    it->addOption(*o_it);
                }
            }

        }
    }
    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
    updatePollData(pollID);
}
void dc_botClient::com_pollRem(SleepyDiscord::Message &message){
    stringVec idStr = regex_FindAll(message.content, "\\d+");
    if(idStr.size() < 2){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
        return;
    }
    int pollID = std::stoi(idStr[0]);
    int optionID = std::stoi(idStr[1]);

    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            //Check if user can remove options:
            if(!(it->author == message.author.username)){
                try {
                    deleteMessage(message.channelID, message.ID);
                } catch (...) {
                    //Already logged through onError()
                }
                return;
            }

            //Remove options:
            it->removeOption(optionID);
            try {
                deleteMessage(message.channelID, message.ID);
            } catch (...) {
                //Already logged through onError()
            }
            updatePollData(pollID);
            return;

        }
    }
}
void dc_botClient::com_pollSet(SleepyDiscord::Message &message){
    //Get pollID:
    stringVec idStrs = regex_FindAll(message.content, "\\d+");
    if(idStrs.size() == 0){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
        return;
    }
    int pollID = std::stoi(idStrs[0]);

    //Get settings:
    stringVec setStrs = regex_FindAll(message.content, "\\w+");
    if(setStrs.size() == 0){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
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
    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
}
void dc_botClient::com_pollClose(SleepyDiscord::Message& message){
    //Get pollID:
    stringVec strIDs = regex_FindAll(message.content, "\\d+");
    if(strIDs.size() == 0){
        try {
            deleteMessage(message.channelID, message.ID);
        } catch (...) {
            //Already logged through onError()
        }
        return;
    }
    int pollID = std::stoi(strIDs[0]);
    //Only poll author can delete poll:
    for(auto& poll : polls){
        if(poll.id == pollID && poll.author != message.author.username){
            try {
                deleteMessage(message.channelID, message.ID);
            } catch (...) {
                //Already logged through onError()
            }
        }
    }

    //Actually delete poll:
    deletePoll(pollID);

    try {
        deleteMessage(message.channelID, message.ID);
    } catch (...) {
        //Already logged through onError()
    }
    evLog.log("Closed poll#" + std::to_string(pollID));
}
void dc_botClient::com_quote(SleepyDiscord::Message &message){
    //Example command: /quote "Name" "Super zitat" "Optionaler Kontext"
    stringVec quoted = regex_FindAll(message.content, "\".+?\"");
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
            quote.append(" \"" + *it + "\"");
        }
        ofile << quote << "\n";
        ofile.close();
    }
    //Send quote to prof-quote channel:
    std::string msg = "**\nPerson:** " + quoted[0];
    msg.append("\n**Zitat:** " + quoted[1]);
    if(quoted.size() == 3){
        msg.append("\n**Kontext:** " + quoted[2]);
    }
    sendMessage("716682386947047455", msg);
    sendMessage(message.channelID, "Saved quote.");
    evLog.log("Saved new quote");
}
void dc_botClient::com_updhelp(SleepyDiscord::Message &message){
    updateHelpMsg();
    sendMessage(message.channelID, "Help message has been updated.");
}

void dc_botClient::com_getLog(SleepyDiscord::Message &message)
{
    std::list<std::string> events;
    stringVec args = strToWords(message.content);
    bool requestedTooManyEvents = false;
    if(args.size() < 2){
        //No amount given. Assume eventCount = 10
        events = evLog.getRecentEvents(10);
    }
    else if(args[1] == trig_getlog[1]){//trig_getlog[1] = "file"
        try {
            uploadFile(message.channelID, configPath + "log.txt", "This file contains all logged events.");
        } catch (...) {
            sendMessage(message.channelID, "Couldn't send log file.");
            evLog.log("Couldn't send log file", ev_log::Level::ERROR);
        }
        return;
    }
    else{
        //Look for numbers in args[1]:
        stringVec nums = regex_FindAll(args[1], "\\d+");
        if(nums.size() > 0){
            int evCount = std::stoi(nums[0]);
            events = evLog.getRecentEvents(evCount);
            if(evCount > evLog.getMaxBufferSize()){
                requestedTooManyEvents = true;
            }
        }
        else{
            sendMessage(message.channelID, "Invalid argument: '" + args[0] + "'");
            return;
        }
    }

    //At this point 'events' contains all available requested events

    std::string msg;
    for(auto& ev : events){
        if(msg.size() + ev.size() >= 2000){
            //Don't exceed max discord message length of 2000 characters!
            break;
        }
        msg.append(ev + " \n");
    }

    if(requestedTooManyEvents){
        msg.append("**There are only " + std::to_string(evLog.getMaxBufferSize()) + " in memory. To download the entire log enter** `" + prefix +
                   trig_getlog[0] + " " + trig_getlog[1] + "`.");
    }
    msg.shrink_to_fit();
    try {
        sendMessage(message.channelID, msg);
    } catch (...) {
        sendMessage(message.channelID, "You have requested too many events. Try fewer or download the entire log via `" + prefix +
                    trig_getlog[0] + " " + trig_getlog[1] + "`.");
        evLog.log("Command '" + message.content + "' failed. Requested too many events.", ev_log::Level::ERROR);
    }

}

//Other
void dc_botClient::loadTextCommands(){
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
            stringVec commands = regex_FindAll(currLine, "'(.*?)'");
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
                    stringVec props = regex_FindAll(pLine, "'(.*?)'");
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
    //Turn all textCommands into Ctriggers:
    stringVec triggers;
    for(auto& tCom : lectureCommands){
        triggers.push_back(tCom.triggers[0]);
    }
    Ctrigger textCmd("textcmd", triggers);
    triggerList.push_back(textCmd);

    evLog.log("Loaded text commands.");
}
void dc_botClient::updateHelpMsg(){
    //Read help_msg.txt and replace matches:
    // '#' are commented lines
    std::string *msg = new std::string();
    std::ifstream ifile;
    ifile.open(configPath + "help_msg.txt");
    if(ifile.is_open()){
        std::string line;
        while(getline(ifile, line)){
            //Process non-empty line:
            if( (line.size() > 0) && (line[0] != '#') ){
                //---Process syntax: '$${<content>}'---
                //Transformation order:
                //    $${`${prefix}${rules}`, }
                //1 =>    `${prefix}${rules}`,
                //2 =>    `$&`,
                //3 =>    `$&`, `$&`, `$&`, ...
                //4 =>    `${prefix}rules`, `${prefix}regeln`, ...
                //Find all multi-identifiers:
                stringVec markedMultiIDs = regex_FindAll(line, "\\$\\$\\{.+\\}");
                for(auto it = markedMultiIDs.begin(); it != markedMultiIDs.end(); ++it){
                    std::string raw_markedID = *it;
                    //step 1:
                    it->erase(it->begin(), it->begin() + 3);//rem '&&{'
                    it->pop_back();//rem '}'
                    //Find identifier and its Ctrigger:
                    stringVec identifiers = regex_FindAll(*it, "\\$\\{\\w+\\}"); //Only sequence second element
                    identifiers[1].erase(identifiers[1].begin(), identifiers[1].begin() + 2);
                    identifiers[1].pop_back();
                    //step 2:
                    findAndReplaceAll(*it, "${prefix}${" + identifiers[1] + "}", "$&");
                    std::string replacePattern;
                    for(auto tr_it = triggerList.begin(); tr_it != triggerList.end(); ++tr_it){
                        if(tr_it->identifier == identifiers[1]){
                            int triggerCount = tr_it->triggers.size();

                            //step 3:
                            for(int i = 0; i < triggerCount; ++i){replacePattern.append(*it);}
                            //step 4:
                            for(int i = 0; i < (int)tr_it->triggers.size(); ++i){
                                //Replace first '$&' each loop:
                                *it = findAndReplaceFirst(replacePattern, "$&", "${prefix}" + tr_it->triggers[i]);
                                replacePattern = *it;
                            }
                        }
                    }                    
                    //Not dynamic but I don't want to think about it too much right now:
                    //Delete last two characters ', ' from *it:
                    it->pop_back();
                    it->pop_back();

                    //Finally, replace multi-identifier with new sequence:
                    findAndReplaceAll(line, raw_markedID, *it);
                }

                //---Process syntax: '${<identifier>}'---
                //Find all identifiers and get their triggers:
                stringVec markedIDs = regex_FindAll(line, "\\$\\{\\w+\\}");
                for(auto currIdentifier : markedIDs){
                    if(currIdentifier != "${prefix}"){
                        currIdentifier.erase(currIdentifier.begin(), currIdentifier.begin() + 2);//rem '${'
                        currIdentifier.pop_back();//rem '}'
                        std::string newTrigger;
                        //Loop through triggerList and get triggers if identifier fits:
                        for(auto it = triggerList.begin(); it != triggerList.end(); ++it){
                            //Get trigger based on identifier if any exists:
                            std::string currTrigger = it->triggerByID(currIdentifier);
                            if(currTrigger.size() > 0 || it == triggerList.end()){
                                newTrigger = currTrigger;
                                break;
                            }
                        }
                        //Replace all occurrences with newTrigger:
                        findAndReplaceAll(line, "${" + currIdentifier + "}", newTrigger);
                    }
                }

                //---Replace prefix---
                findAndReplaceAll(line, "${prefix}", prefix);

            }
            if(line.size() == 0){
                msg->append("\n");
            }
            else if(line[0] != '#'){
                msg->append(line + "\n");
            }
        }
    }

    //Update messages:
    help_msg = *msg;
#ifdef NDEBUG
    editMessage("702968771735978194", "702969362679857283", *msg);
#endif
    //delete msg;
    evLog.log("Updated help message.");
}

void dc_botClient::updateIPInfo(){
    std::string ip = getIP();
    sendMessage("702765369940639879", "IP: **" + ip + "**");
}
int dc_botClient::getPollID(){
    nextPollID++;
    return nextPollID - 1;
}
void dc_botClient::updatePollData(const int pollID){
    //Get poll:
    for(auto poll : polls){
        if(poll.id == pollID){

            std::string topicPre;
            std::string topicSuf;
            if(poll.isClosed){
                topicPre = "```diff\n- [GESCHLOSSEN] ";
                topicSuf = "\n```";
            }
            else{
                topicPre = "```diff\n+ ";
                topicSuf = "\n```";
            }

            std::string pollMsg = "\nUmfrage **#" + std::to_string(poll.id) + "** von **" + poll.author + "**\n";
            pollMsg.append(topicPre + poll.topic + topicSuf + "\n");
            for(auto& option : poll.options){
                pollMsg.append("**" + std::to_string(option.id) + ":** " + option.value + "    **" +
                               std::to_string(poll.getOptPercentage(option.id)) + "%** (" +
                               std::to_string(option.voteCount) + "/" + std::to_string(poll.totalVotes()) + ")\n");
            }

            pollMsg.append("\nMultiple Choice (`" + trig_poll[8] + "`): ");
            if(poll.allowMultipleChoice){
                pollMsg.append("Ja.\n");
            }else{
                pollMsg.append("Nein.\n");
            }
            pollMsg.append("Eigene Antworten erlaubt (`" + trig_poll[7] + "`): ");
            if(poll.allowCustOpt){
                pollMsg.append("Ja.\n");
            }else{
                pollMsg.append("Nein.\n");
            }

            if(!poll.isClosed){
                pollMsg.append("\nAuswahl mit `" + prefix + trig_poll[1] + " " + std::to_string(poll.id) + " <option_ID>`\n");
                pollMsg.append("Einstellungen ändern mit `" + prefix + trig_poll[6] + " " + std::to_string(poll.id) + " <setting1> <setting2> ...`");
            }else{
                pollMsg.append("\nUmfrage wurde geschlossen.");
            }
            if(!poll.messageExists){
                auto newMessage = sendMessage(poll.pollChannelID, pollMsg);
                poll.pollMessageID = newMessage.cast().ID;
                poll.messageExists = true;
            }else{
                try {
                    editMessage(poll.pollChannelID, poll.pollMessageID, pollMsg);
                } catch (...) {
                    auto newMessage = sendMessage(poll.pollChannelID, pollMsg);
                    poll.pollMessageID = newMessage.cast().channelID;
                    poll.pollMessageID = newMessage.cast().ID;
                }
            }

            //Save poll to disk:
            savePoll(poll);
#ifndef NDEBUG
            //Logmessage:
            std::string logMsg = "Updated poll#" + std::to_string(poll.id);
            for(auto it = poll.options.begin(); it != poll.options.end(); ++it){
                logMsg.append("-" + std::to_string(it->voteCount));
            }
            evLog.log(logMsg);
#endif
        }
    }

}
void dc_botClient::loadAllPolls(){

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

    //Polls on disc might have gotten new IDs after loading.
    //Go through all entries in poll_list.txt and delete any polls whose
    //IDs don't exist in memory. Polls in memory will already be resaved with
    //their correct IDs later on.
    //THIS HAS OPTIMISATION POTENTIAL

    std::ifstream pollList;
    std::string currLine;
    stringVec newEntryList;
    pollList.open(configPath + "poll_list.txt");
    if(pollList.is_open()){
        while(getline(pollList, currLine)){
            stringVec IDStrs = regex_FindAll(currLine, "\\d+");
            bool pollIsInMemory = false;
            if(IDStrs.size() > 0){
                int currID = std::stoi(IDStrs[0]);
                for(auto& currPoll : polls){
                    if(currPoll.id == currID){
                        pollIsInMemory = true;
                        break;
                    }
                }
                if(!pollIsInMemory){
                    std::remove((configPath + "polls/" + currLine).c_str());
                }
                else{
                    newEntryList.push_back(currLine);
                }
            }
        }
        pollList.close();
        //Delete poll_list.txt and recreate it with correct content:
        std::remove((configPath + "poll_list.txt").c_str());
        std::ofstream newList;
        newList.open(configPath + "poll_list.txt");
        if(newList.is_open()){
            for(auto& entry : newEntryList){
                newList << entry << "\n";
            }
            newList.close();
        }
    }

    evLog.log("Loaded " + std::to_string(paths.size()) + " polls from disk.");

}
void dc_botClient::savePoll(mo_poll& poll){
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

void dc_botClient::checkExpiredPolls()
{
    schedule([this](){this->checkExpiredPolls();}, 600000);//Execute every 10 minutes
    evLog.log("Checking for expired polls.");
    time_t currTime = time(0);
    for(auto& poll : polls){
#ifndef NDEBUG
        evLog.log("Poll#" + std::to_string(poll.id) +
                  " expires in " + std::to_string(difftime(poll.expiryTime, currTime)), ev_log::Level::DEBUG);
#endif
        if(difftime(poll.expiryTime, currTime) < 0){
            //Poll has expired
            deletePoll(poll.id);
        }
    }
}
void dc_botClient::deletePoll(const int pollID){
    //Find poll with pollID:
    for(auto it = polls.begin(); it != polls.end(); ++it){
        if(it->id == pollID){
            it->isClosed = true;

            //Delete from disk:
            //Read poll_list.txt into memory and write it back
            //except for the entry to be deleted:
            std::ifstream poll_inFile;
            poll_inFile.open(configPath + "poll_list.txt");
            if(poll_inFile.is_open()){
                stringVec listBuffer;
                std::string line;
                while(getline(poll_inFile, line)){
                    if(line != "poll_" + std::to_string(pollID) + ".txt"){
                        listBuffer.push_back(line);
                    }
                }
                poll_inFile.close();
                //Delete file and rewrite it:
                std::remove((configPath + "poll_list.txt").c_str());
                std::ofstream poll_ofFile;
                poll_ofFile.open(configPath + "poll_list.txt");
                if(poll_ofFile.is_open()){
                    for(auto& line : listBuffer){
                        poll_ofFile << line << "\n";
                    }
                    poll_ofFile.close();
                }
            }

            //Delete actual poll file:
            std::remove((configPath + "polls/poll_" + std::to_string(pollID) + ".txt").c_str());

            //Update poll message one last time:
            updatePollData(pollID);

            //Delete from memory:
            polls.erase(it);
            evLog.log("Deleted poll#" + std::to_string(pollID));
            return;
        }
    }
}
