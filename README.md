# About

This repository contains the source code to my discord bot. I have written it primarly to fit my own needs so others can't just use this code as is. There are functions that e.g. send messages to hard coded channel-IDs. If you really want to use this code and you don't know or don't want to go through all of it then we can talk about making it more accessible, no promises though.

## Branches

To get the lowest possibility of bugs and crashes then you should only use the master branch. I only commit code there if I at least feel like it works half stable, which doesn't mean that it is free of bugs or doesn't crash.

# Installation:

## Download
 - Download all files and save them in a directory (e.g. `~/discord_bot`)
 - Or just clone the repo: `git clone https://github.com/EVARATE/discord_bot.git`
 - In the terminal go to that directory
## Dependencies
 - Get [sleepy-discord](https://github.com/yourWaifu/sleepy-discord.git):  `git clone https://github.com/yourWaifu/sleepy-discord.git`
## Build
 - Create build-folder: `mkdir build`
 - Go into that folder: `cd build`
 - Run `cmake ..`
 - Run `make`

**If cmake returned errors** do this:
 - Change directory to `sleepy-discord/deps`. If the folders `asio`, `cpr` and `websocketpp` are empty clone the following repositories:
   - [Asio](https://github.com/chriskohlhoff/asio.git):  `git clone https://github.com/chriskohlhoff/asio.git`
   - [CPR](https://github.com/whoshuu/cpr.git):  `git clone https://github.com/whoshuu/cpr.git`
   - [WebSocket++](https://github.com/zaphoyd/websocketpp.git):  `git clone https://github.com/zaphoyd/websocketpp.git`
 - Now change directory to `sleepy-discord/deps/cpr/opt`. If the folder `curl` is empty clone the following repository:
   - [curl](https://github.com/curl/curl.git):  `git clone https://github.com/curl/curl.git`
 - Repeat the build process

Now you have a `discord_bot` executable which can be run with `./discord_bot`

# External Resources:
 - [sleepy-discord](https://github.com/yourWaifu/sleepy-discord) C++ library
