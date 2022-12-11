cmake_minimum_required(VERSION 3.12)
project(fiatlux)
set(CMAKE_CXX_STANDARD 17)

if(NOT IMGUI_BUNDLE_BUILD_FIATLUX)
    include(cmake/fetch_imgui_bundle.cmake)
endif()

# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")


##########################################################
# Build your app
##########################################################
# Call imgui_bundle_add_app
imgui_bundle_add_app(fiat_hello fiat_hello.main.cpp)

# Now you can build your app with
#     mkdir build && cd build && cmake .. && cmake --build .
