cmake_minimum_required(VERSION 3.12)
project(fiatlux)
set(CMAKE_CXX_STANDARD 17)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/fetch_imgui_bundle.cmake)

add_subdirectory(cpp/fiatlux)
add_subdirectory(demos)
