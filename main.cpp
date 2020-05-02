#include <iostream>
#include <fstream>
#include "myclientclass.h"



int main()
{
    MyClientClass client("NzAyNzU4OTg5MjcxNjYyNjMy.Xq1pDQ.oVq9Ex2g_HvyHpxfGSX8DvwIi9Y",2);
    client.setupData();
    client.run();
}
