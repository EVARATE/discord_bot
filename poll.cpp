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
void mo_poll::voteForOption(const int id){
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id){
            it->voteCount++;
            return;
        }
    }
}
void mo_poll::unvoteForOption(const int id){
    for(auto it = options.begin(); it != options.end(); ++it){
        if(it->id == id && it->voteCount > 0){
            it->voteCount--;
            return;
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

int mo_poll::getOptID(){
    nextID++;
    return nextID - 1;
}
