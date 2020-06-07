#include "../HEADERS/poll.h"


void mo_poll::addOption(const std::string &newOption){
    if(newOption.size() != 0){
        pollOption opt;
        opt.id = getOptID();
        opt.value = newOption;
        options.push_back(opt);
    }
}
void mo_poll::removeOption(const int id){
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id){
            options.erase(it);
            return;
        }
    }
}
void mo_poll::voteForOption(const int id, const std::string& voterID){
    if(!hasVoted(voterID) || allowMultipleChoice){
        for(auto it = options.begin(); it != options.end(); ++it){
            if(it->id == id){
                if(it->opt_hasVoted(voterID)){return;}
                it->voteCount++;
                //Add voterID:
                it->voterIDs.push_back(voterID);
                return;
            }
        }
    }
}
void mo_poll::unvoteForOption(const int id, const std::string& voterID){
    for(auto it = options.begin(); it != options.end(); ++it){
        if((it->id == id) && (it->voteCount > 0) && it->opt_hasVoted(voterID)){
            it->voteCount--;
            //Remove voterID:
            for(int i = 0; i < (int)it->voterIDs.size(); ++i){
                if(it->voterIDs[i] == voterID){
                    it->voterIDs.erase(it->voterIDs.begin() + i);
                }
            }
        }
    }
}

int mo_poll::getOptPercentage(const int id){
    //Get total votes:
    int totalVotes = 0;
    for(auto it = options.begin(); it != options.end(); ++it){
        totalVotes += it->voteCount;
    }
    if(totalVotes == 0){
        return 0;
    }
    //Get votes of option with id:
    int optionVotes = 0;
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id){
            optionVotes = it->voteCount;
        }
    }
    return std::abs((double)optionVotes / (double)totalVotes) * 100.0;
}

int mo_poll::totalVotes()
{
    //Go through all options and count votes:
    int totVotes = 0;
    for(auto it = options.begin(); it != options.end(); ++it){
        totVotes += it->voteCount;
    }
    return totVotes;
}
bool mo_poll::hasVoted(const std::string &voterID){
    //Loop through all options and see if voter exists with voterID:
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->opt_hasVoted(voterID)){
            return true;
        }
    }
    return false;
}

void mo_poll::loadPoll(const std::string &filePath){
    std::ifstream ifile;
    ifile.open(filePath);
    if(!ifile.is_open()){return;}

    //Topic:
    std::string lineBuffer;
    getline(ifile, lineBuffer);
    lineBuffer.erase(lineBuffer.begin());//Remove "'"
    lineBuffer.pop_back();//Remove last "'"
    topic = lineBuffer;
    //Author:
    getline(ifile, lineBuffer);
    lineBuffer.erase(lineBuffer.begin());//Remove "'"
    lineBuffer.pop_back();//Remove last "'"
    author = lineBuffer;
    //pollChannelID:
    getline(ifile, lineBuffer);
    pollChannelID = lineBuffer;
    //pollMessageID:
    getline(ifile, lineBuffer);
    pollMessageID = lineBuffer;
    //messageExists:
    getline(ifile, lineBuffer);
    messageExists = intToBool(std::stoi(lineBuffer));
    //isClosed:
    getline(ifile, lineBuffer);
    isClosed = intToBool(std::stoi(lineBuffer));
    //allowCustOpt:
    getline(ifile, lineBuffer);
    allowCustOpt = intToBool(std::stoi(lineBuffer));
    //allowMultipleChoice:
    getline(ifile, lineBuffer);
    allowMultipleChoice = intToBool(std::stoi(lineBuffer));

    //Load all options data:
    int highestOptID = 0;
    while(getline(ifile, lineBuffer)){
        if(lineBuffer[0] == 'o'){
            //Get optionID:
            auto idStrVec = returnMatches(lineBuffer, "\\d+");
            int optionID = std::stoi(idStrVec[0]);
            highestOptID = std::max(highestOptID, optionID);
            //Get quoted things:
            auto quoteVec = returnMatches(lineBuffer, "'.+?'");
            //Create pollOption and save it to the class:
            pollOption currOption;
            currOption.id = optionID;
            currOption.value = quoteVec[0].substr(1, quoteVec[0].size() - 2);
            if(quoteVec.size() > 1){
                for(auto ID_it = quoteVec.begin() + 1; ID_it != quoteVec.end(); ++ID_it){
                    std::string currID = *ID_it;
                    currID.erase(currID.begin());
                    currID.pop_back();
                    currOption.voterIDs.push_back(currID);
                    currOption.voteCount++;
                }
            }
            options.push_back(currOption);
        }
    }
    ifile.close();
    //New options must have valid IDs:
    nextID = highestOptID + 1;


    /* EXAMPLE FILE:
     *
     * 'My topic'
     * 'Username_author'
     * 492734023423423434
     * 342348048023948576
     * 1
     * 0
     * 1
     * 1
     * o 0 'First option' '123412341231232323' '442934892348023433' '534959359340570349'
     * o 1 'Second option' '243923049820394834' '594934759374598023'
     * o 2 'Third option'
     * o 3 'Fourth option' '230498032840293485'
     *
     */
}
void mo_poll::savePoll(const std::string &filePath){
    std::remove(filePath.c_str());
    std::ofstream ofile;
    ofile.open(filePath);
    if(!ofile.is_open()){return;}
    //Data:
    ofile << "'" + topic + "'\n";
    ofile << "'" + author + "'\n";
    ofile << pollChannelID + "\n";
    ofile << pollMessageID + "\n";
    ofile << messageExists << "\n";
    ofile << isClosed << "\n";
    ofile << allowCustOpt << "\n";
    ofile << allowMultipleChoice << "\n";

    //For each option:
    for(auto currOption = options.begin(); currOption != options.end(); ++currOption){
        ofile << "o " << currOption->id << " '" << currOption->value << "'";
        for(auto v_it = currOption->voterIDs.begin(); v_it != currOption->voterIDs.end(); ++v_it){
            ofile << " '" << *v_it << "'";
        }
        ofile << "\n";
    }
    ofile.close();
}

int mo_poll::getOptID(){
    nextID++;
    return nextID - 1;
}

//POLLOPTION IMPLEMENTATION:

bool pollOption::opt_hasVoted(const std::string &voterID){
    for(auto it = voterIDs.begin(); it != voterIDs.end(); ++it){
        if(*it == voterID){
            return true;
        }
    }
    return false;
}
