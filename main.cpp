#include <iostream>
#include <fstream>
#include "commandclient.h"

int main()
{
    commandClient comClient("NzAyNzU4OTg5MjcxNjYyNjMy.Xq2-Vw.6OODmTwe-lc9QA7VreQHKVPJSCs",2);
    comClient.setupData();
    comClient.run();


}
