#include "poll.h"


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
    //First explicitly saved optionID:
    getline(ifile, lineBuffer);
    int lastOptID = std::stoi(lineBuffer);

    //Load all options data:
    bool firstLineOfOption = true;
    while(!ifile.eof()){
        getline(ifile, lineBuffer);
        if(lineBuffer.size() > 0){
            //Get optionID and values:
            std::regex idReg("\\d+");
            int currOptID = std::stoi(returnMatches(lineBuffer, idReg)[0]);
            std::regex valReg("'.+'");
            auto vals = returnMatches(lineBuffer, valReg);
            std::string currOptValue = vals[0];
            currOptValue.erase(currOptValue.begin());
            currOptValue.pop_back();
            pollOption currOption;
            if(currOptID == lastOptID){
                currOption.id = currOptID;
                if(firstLineOfOption){
                    currOption.value = currOptValue;
                    firstLineOfOption = false;
                }else{
                    currOption.voterIDs.push_back(currOptValue);
                }
            }
            else{
                firstLineOfOption = true;
                options.push_back(currOption);
                currOption = pollOption();//Empty currOption
            }
        }
    }
    ifile.close();


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
     * 0
     * o 0 'First option'
     * o 0 '123412341231232323'
     * o 0 '442934892348023433'
     * o 0 '534959359340570349'
     * o 1 'Second option'
     * o 1 '243923049820394834'
     * o 1 '594934759374598023'
     * o 2 'Third option'
     * o 3 'Fourth option'
     * o 3 '230498032840293485'
     *
     */
}
void mo_poll::savePoll(const std::string &filePath){
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
    ofile << options.begin()->id << "\n";//Save first optionID extra to make loading easier

    //For each option:
    for(auto currOption = options.begin(); currOption != options.end(); ++currOption){
        std::string optPrefix = "o " + std::to_string(currOption->id);
        ofile << optPrefix << " '" + currOption->value + "'\n";
        //For each voterID in this option:
        for(auto currVoterID = currOption->voterIDs.begin(); currVoterID != currOption->voterIDs.end(); ++currVoterID){
            ofile << optPrefix << " '" << *currVoterID << "'\n";
        }
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
