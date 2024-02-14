#include "fiatlux/computer_vision/image_with_gui.h"
#include "fiatlux/computer_vision/lut.h"
#include "immapp/immapp.h"

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

namespace VisualProg
{
    struct GaussianBlurWithGui : public VisualProg::FunctionWithGui
    {
        float sigmaX = 3.f;
        float sigmaY = 3.f;

        GaussianBlurWithGui()
        {
            auto &self = *this;
            self.InputGui = std::make_shared<ImageWithGui>();
            self.OutputGui = std::make_shared<ImageWithGui>();
        }

        std::any f(const std::any &x) override
        {
            auto &self = *this;
            const Image &asImage = std::any_cast<const Image &>(x);
            cv::Size ksize(0, 0);
            cv::Mat blur;
            cv::GaussianBlur(asImage, blur, ksize, self.sigmaX, self.sigmaY);
            return blur;
        }

        std::string Name() override { return "GaussianBlur"; }

        bool GuiParams() override
        {
            auto &self = *this;
            bool changed = false;
            ImGui::SetNextItemWidth(100.f);
            changed |= ImGui::SliderFloat("sigmaX", &self.sigmaX, 0.1, 15.0);
            ImGui::SetNextItemWidth(100.f);
            changed |= ImGui::SliderFloat("sigmaY", &self.sigmaY, 0.1, 15.0);
            return changed;
        }
    };

    struct CannyWithGui : public FunctionWithGui
    {
        int tLower = 100; // Lower threshold
        int tUpper = 200; // Upper threshold
        int apertureSize = 5; // Aperture size (3, 5, or 7)

        CannyWithGui()
        {
            auto &self = *this;
            self.InputGui = std::make_shared<ImageWithGui>();
            self.OutputGui = std::make_shared<ImageWithGui>();
        }

        std::any f(const std::any &x) override
        {
            auto &self = *this;
            const Image &asImage = std::any_cast<const Image &>(x);
            cv::Size ksize(0, 0);
            cv::Mat edge;
            cv::Canny(asImage, edge, self.tLower, self.tUpper, self.apertureSize);
            return edge;
        }

        std::string Name() override
        { return "Canny"; }

        bool GuiParams() override
        {
            auto &self = *this;
            bool changed = false;
            ImGui::SetNextItemWidth(100.f);
            changed |= ImGui::SliderInt("tLower", &self.tLower, 0, 255);
            ImGui::SetNextItemWidth(100.f);
            changed |= ImGui::SliderInt("tUpper", &self.tUpper, 0, 255);

            ImGui::Text("Aperture");
            ImGui::SameLine();

            std::vector<int> apertures{3, 5, 7};
            for (int aperture_value: apertures)
            {
                changed |= ImGui::RadioButton(std::to_string(aperture_value).c_str(), &self.apertureSize,
                                              aperture_value);
                ImGui::SameLine();
            }
            ImGui::NewLine();
            return changed;
        }
    };
}

int main(int, char**)
{
    using namespace VisualProg;

    auto file = HelloImGui::AssetFileFullPath("images/house.jpg");
    cv::Mat image = cv::imread(file);
    cv::resize(image, image, cv::Size(), 0.5, 0.5);

    auto split_lut_merge_gui = Split_Lut_Merge_WithGui(ColorType::BGR);

    std::vector<FunctionWithGuiPtr> functions;
    functions = { split_lut_merge_gui._split, split_lut_merge_gui._lut, split_lut_merge_gui._merge};
    // functions = { std::make_shared<GaussianBlurWithGui>(), std::make_shared<CannyWithGui>() };

    FunctionsCompositionGraph compositionGraph(functions);
    compositionGraph.SetInput(image);

    auto gui = [&](){
        compositionGraph.Draw();
    };

    ImmApp::AddOnsParams addOnsParams;
    ax::NodeEditor::Config nodeEditorConfig;
    nodeEditorConfig.SettingsFile = "demo_compose_image.json";

    addOnsParams.withNodeEditorConfig = nodeEditorConfig;
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = gui;
    params.windowSize = {1600, 1000};
    ImmApp::Run(params, addOnsParams);

    return 0;
}