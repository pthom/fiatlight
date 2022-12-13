cmake_minimum_required(VERSION 3.12)
project(fiatlux)
set(CMAKE_CXX_STANDARD 17)

if(NOT IMGUI_BUNDLE_BUILD_FIATLUX)
    include(cmake/fetch_imgui_bundle.cmake)
endif()
add_subdirectory(src/fiatlux)
add_subdirectory(demos)