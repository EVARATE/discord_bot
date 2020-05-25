#include "poll.h"

mo_poll::mo_poll()
{
    //Constructor does nothing yet. Be careful when using this!!
}

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
    if(hasVoted(voterID)){return;}
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id){
            it->voteCount++;
            //Add voterID:
            voterIDs.push_back(voterID);
            return;
        }
    }
}
void mo_poll::unvoteForOption(const int id, const std::string& voterID){
    if(!hasVoted(voterID)){return;}
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id && it->voteCount > 0){
            it->voteCount--;
            //Remove voterID:
            for(auto v_it = voterIDs.begin(); v_it != voterIDs.end(); ++v_it){
                if(*v_it == voterID){
                    voterIDs.erase(v_it);
                    return;
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
bool mo_poll::hasVoted(const std::string &voterID){
    if(voterIDs.size() == 0){return false;}

    for(auto it = voterIDs.begin(); it != voterIDs.end(); ++it){
        if(*it == voterID){
            return true;
        }
    }
    return false;
}

int mo_poll::getOptID(){
    nextID++;
    return nextID - 1;
}
