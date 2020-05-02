cmake_minimum_required(VERSION 3.5)

project(discord_bot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(discord_bot main.cpp myclientclass.cpp myclientclass.h)

add_subdirectory(sleepy-discord/)
target_link_libraries(discord_bot sleepy-discord)

