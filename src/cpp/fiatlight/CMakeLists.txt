file(GLOB_RECURSE sources *.h *.cpp)
add_library(fiatlight ${sources})
target_link_libraries(fiatlight PUBLIC imgui immvision imgui_node_editor immapp)
target_include_directories(fiatlight PUBLIC ${CMAKE_CURRENT_LIST_DIR}/..)
