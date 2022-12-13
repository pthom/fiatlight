file(GLOB_RECURSE sources *.h *.cpp)
add_library(fiatlux ${sources})
target_link_libraries(fiatlux PUBLIC imgui immvision imgui_node_editor immapp)
target_include_directories(fiatlux PUBLIC ${CMAKE_CURRENT_LIST_DIR}/..)
