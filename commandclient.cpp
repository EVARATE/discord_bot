#include "commandclient.h"


//Session actions
void commandClient::onMessage(SleepyDiscord::Message message){
    //Split command into words:
    auto commandLower = toLowerCase(message.content);
    commandLower.erase(0, prefix.size());
    auto command = toWords(message.content);

    //Look for commands:
    if(message.startsWith(prefix)){
        //Check for text commands:
        execTextCommand(command, message);
    }
}
void commandClient::onReady(std::string *jsonMessage){

}
void commandClient::onDisconnect(){

}
void commandClient::onResume(){

}

//Commands
void commandClient::execTextCommand(stringVec &command, SleepyDiscord::Message &message){

}

//Other
void commandClient::loadTextCommands(){
    std::ifstream ifile;
    ifile.open(configPath + "textCommands.txt");
    if(!ifile.is_open()){return;}
}
