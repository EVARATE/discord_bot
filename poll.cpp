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
    //Load data:
    ifile >> id;
    ifile >> nextID;
    std::string topicStr;
    getline(ifile, topicStr);
    topicStr.erase(topicStr.begin());//Delete quotation marks
    topicStr.pop_back();
    ifile >> author;
    ifile >> pollChannelID;
    ifile >> pollMessageID;
    ifile >> messageExists;
    ifile >> isClosed;
    bool readOptions = true;
    while(readOptions){
        std::string line;
        getline(ifile, line);
        if(line[0] == '-'){
            line.erase(line.begin());//Delete '-'
            //Example: custopt 1
            stringVec custWords = strToWords(line);
            if(custWords[0] == "custopt"){
                allowCustOpt = intToBool(std::stoi(custWords[1]));
            }
            if(custWords[0] == "multi"){
                allowMultipleChoice = intToBool(std::stoi(custWords[1]));
            }
        }else{
            readOptions = false;
        }
    }
    //================CONTINUE HERE===============================================

    ifile.close();
}
void mo_poll::savePoll(const std::string &filePath){
    std::ofstream ofile;
    ofile.open(filePath);
    if(!ofile.is_open()){return;}
    //Save data:
    ofile << id << "\n";
    ofile << nextID << "\n";
    ofile << "'" << topic << "'\n";
    ofile << author << "\n";
    ofile << pollChannelID << "\n";
    ofile << pollMessageID << "\n";
    ofile << messageExists << "\n";
    ofile << isClosed << "\n";
    //Settings:
    ofile << "-custopt " << allowCustOpt << "\n";
    ofile << "-multi " << allowMultipleChoice << "\n";
    //Options:
    for(auto it = options.begin(); it != options.end(); ++it){
        ofile << "option\n";
        ofile << it->id << "\n";
        ofile << "'" << it->value << "'\n";
        //Save voterIDs:
        for(auto v_it = it->voterIDs.begin(); v_it != it->voterIDs.end(); ++v_it){
            ofile << "v " << *v_it << "\n";
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
