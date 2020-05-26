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
