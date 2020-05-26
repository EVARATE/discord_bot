#ifndef POLL_H
#define POLL_H
#include <vector>
#include <string>

typedef struct{
    int id;
    int voteCount = 0;
    std::string value;
    std::vector<std::string> voterIDs;

    bool opt_hasVoted(const std::string& voterID);

}pollOption;

class mo_poll
{
public:
    mo_poll(const std::string question, std::vector<std::string>& pollOptions):
        topic(question)
    {
        for(auto it = pollOptions.begin(); it != pollOptions.end(); ++it){
            addOption(*it);
        }
    }

    void addOption(const std::string& newOption);
    void removeOption(const int id);
    void voteForOption(const int id, const std::string& voterID);
    void unvoteForOption(const int id, const std::string& voterID);

    int getOptPercentage(const int id);
    int totalVotes();
    bool hasVoted(const std::string& voterID);

    std::vector<pollOption> getCurrOptions();

    int getOptID();
    int id;
    std::string topic;
    std::vector<pollOption> options;

    //Metadata
    std::string author = "";
    std::string pollChannelID = "";
    std::string pollMessageID = "";
    bool messageExists = false;
    bool isClosed = false;
    bool allowCustOpt = false;
    bool allowMultipleChoice = false;
private:
    int nextID = 1;
};

#endif // POLL_H
