#include <iostream>
#include <fstream>
#include "commandclient.h"

int main()
{
    //Get token from file:
    std::ifstream ifile;
    ifile.open("token.txt");
    std::string token;
    if(ifile.is_open()){
        ifile >> token;
        fprintf(stderr, "Reading token\n");
        ifile.close();
    }
    if(token.length() != 59){
        std::string error = "ERROR: Invalid token: '" + token + "'. Enter token in 'token.txt' file\n";
        fprintf(stderr, error.c_str());
        return 0;
    }

    commandClient comClient(token,2);
    comClient.setupData();
    comClient.run();


}
