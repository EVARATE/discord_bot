cmake_minimum_required(VERSION 3.5)

project(discord_bot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(discord_bot
    main.cpp
    dc_botClient.cpp
    dc_botClient.h
    miscCode.cpp
    poll.h
    poll.cpp
    event_log.h
    event_log.cpp
    )

add_subdirectory(sleepy-discord/)
target_link_libraries(discord_bot sleepy-discord)

