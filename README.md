# Installation:

## Download
 - Download all files and save them in a directory (e.g. `~/home/discord_bot`)
 - In the terminal go to that directory
## Dependencies
 - Change directory to `sleepy-discord/deps`. If the folders `asio`, `cpr` and `websocketpp` are empty clone the following repositories:
   - [Asio](https://github.com/chriskohlhoff/asio.git):  `git clone https://github.com/chriskohlhoff/asio.git`
   - [CPR](https://github.com/whoshuu/cpr.git):  `git clone https://github.com/whoshuu/cpr.git`
   - [WebSocket++](https://github.com/zaphoyd/websocketpp.git):  `git clone https://github.com/zaphoyd/websocketpp.git`
 - Now change directory to `sleepy-discord/deps/cpr/opt`. If the folder `curl` is empty clone the following repository:
   - [curl](https://github.com/curl/curl.git):  `git clone https://github.com/curl/curl.git`
## Build
 - Go back to `discord_bot`
 - Create build-folder: `mkdir build`
 - Go into that folder: `cd build`
 - Run `cmake ..`
 - Run `make`

Now you have a `discord_bot` executable which can be run with `./discord_bot`

# External Resources:
 - [sleepy-discord](https://github.com/yourWaifu/sleepy-discord) C++ library
