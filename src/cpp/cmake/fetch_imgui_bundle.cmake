# 1/  Option 1: if you added imgui_bundle in a subfolder, you can add it to your project with:
if(IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/external/imgui_bundle)
    add_subdirectory(external/imgui_bundle)
endif()

## 2/  Option 2: simply fetch imgui_bundle during the build
if (NOT TARGET imgui_bundle)
    message(STATUS "Fetching imgui_bundle...")
    include(FetchContent)
    Set(FETCHCONTENT_QUIET FALSE)
    FetchContent_Declare(imgui_bundle GIT_REPOSITORY https://github.com/pthom/imgui_bundle.git GIT_TAG main)
    FetchContent_MakeAvailable(imgui_bundle)
    set(IMMVISION_FETCH_OPENCV ON)
endif()
