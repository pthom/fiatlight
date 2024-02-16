set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

imgui_bundle_add_app(fiat_add fiat_add.main.cpp)
target_link_libraries(fiat_add PUBLIC fiatlight)

imgui_bundle_add_app(fiat_image fiat_image.main.cpp)
target_link_libraries(fiat_image PUBLIC fiatlight)
