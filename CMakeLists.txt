cmake_minimum_required(VERSION 3.5)

project(discord_bot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(discord_bot
    HEADERS/dc_botClient.h
    HEADERS/poll.h
    HEADERS/ev_log.h
    HEADERS/quote_handler.h
    SOURCES/main.cpp
    SOURCES/miscCode.cpp
    SOURCES/dc_botClient.cpp
    SOURCES/poll.cpp
    SOURCES/ev_log.cpp
    SOURCES/quote_handler.cpp
    )

add_subdirectory(deps/sleepy-discord/)
target_link_libraries(discord_bot sleepy-discord)

