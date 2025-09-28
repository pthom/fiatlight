import fiatlight as fl
import pandas as pd
from enum import Enum
from imgui_bundle import implot, hello_imgui
import numpy as np


def make_titanic_dataframe() -> pd.DataFrame:
    # Here, we provide an example data frame to the user,
    # using the Titanic dataset from the Data Science Dojo repository.
    # (widely used in data science tutorials)
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Error loading sample dataset: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of failure
    return df


TITANIC_DATAFRAME = make_titanic_dataframe()


class Sex(Enum):
    Man = "male"
    Woman = "female"


@fl.with_fiat_attributes(
    # define the fiat attributes for the function parameters
    label="Titanic Data",
    age_min__range=(0, 100),
    age_max__range=(0, 100),
    passenger_class__range=(1, 3),
    passenger_class__label="Passenger Class",
    # define fiat attributes for the function output
    # (i.e. the presentation options for the DataFrame)
    return__widget_size_em=(55.0, 15.0),
    return__rows_per_page_node=15,
    return__rows_per_page_popup=20,
    return__column_widths_em={"Name": 5},
)
def show_filterable_dataframe(
    passenger_class: int | None = None,
    survived: bool | None = None,
    sex: Sex | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> pd.DataFrame:
    dataframe = TITANIC_DATAFRAME
    if dataframe.empty:
        return dataframe

    # filter dataframe
    if survived is not None:
        dataframe = dataframe[dataframe["Survived"] == int(survived)]
    if passenger_class is not None:
        dataframe = dataframe[dataframe["Pclass"] == passenger_class]
    if sex:
        dataframe = dataframe[dataframe["Sex"] == sex.value]
    if age_min is not None:
        dataframe = dataframe[dataframe["Age"] >= age_min]
    if age_max is not None:
        dataframe = dataframe[dataframe["Age"] <= age_max]

    return dataframe


@fl.with_fiat_attributes(label="Survival Rate")
def survival_rate_plot(df: pd.DataFrame) -> None:
    total = df["Survived"].count()
    if total == 0:
        return
    survived_count = df["Survived"][df["Survived"] == 1].count()
    dead_count = total - survived_count
    percents = np.array([survived_count / total * 100.0, dead_count / total * 100.0])
    labels = ["Survived", "Died"]
    if implot.begin_plot("Survival Rate", size=hello_imgui.em_to_vec2(20.0, 20.0)):
        implot.plot_pie_chart(label_ids=labels, values=percents, x=0.5, y=0.5, radius=0.4, label_fmt="%.1f%%")
        implot.end_plot()


@fl.with_fiat_attributes(label="Age Histogram")
def age_histogram_plot(df: pd.DataFrame) -> None:
    if df.empty or "Age" not in df.columns:
        return
    if implot.begin_plot("Age Distribution", size=hello_imgui.em_to_vec2(30.0, 20.0)):
        implot.setup_axes(
            x_label="Age",
            y_label="Count",
            x_flags=implot.AxisFlags_.auto_fit,
            y_flags=implot.AxisFlags_.auto_fit,
        )
        implot.plot_histogram("Age", df["Age"].dropna().values, bins=30)  # type: ignore
        implot.end_plot()


def main() -> None:
    graph = fl.FunctionsGraph()
    graph.add_function(show_filterable_dataframe)

    graph.add_gui_node(age_histogram_plot)
    graph.add_link(show_filterable_dataframe, age_histogram_plot)

    graph.add_gui_node(survival_rate_plot)
    graph.add_link(show_filterable_dataframe, survival_rate_plot)

    fl.run(graph, app_name="dataframe_with_gui_demo_titanic")


if __name__ == "__main__":
    main()
