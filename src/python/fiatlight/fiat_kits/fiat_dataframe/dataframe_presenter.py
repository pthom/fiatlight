import copy

from pydantic import BaseModel, Field
import pandas as pd
from fiatlight.fiat_core.possible_custom_attributes import PossibleCustomAttributes
from fiatlight.fiat_types import CustomAttributesDict, JsonDict
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx, icons_fontawesome_6
from imgui_bundle import imgui, imgui_ctx, hello_imgui
from typing import List


class DataFramePossibleCustomAttributes(PossibleCustomAttributes):
    # Here we will add all the possible custom attributes for the DataFrame
    # so that the user can customize the presentation of the DataFrame
    # (probably by settings params in DataFramePresenterParams)
    def __init__(self) -> None:
        super().__init__("DataFrameWithGui")


_DATAFRAME_POSSIBLE_CUSTOM_ATTRIBUTES = DataFramePossibleCustomAttributes()


class DataFramePresenterParams(BaseModel):
    # Widget size in em
    widget_size_em: tuple[float, float] = (20.0, 20.0)

    # Dictionary to specify custom widths for individual columns, identified by column name.
    column_widths_em: dict[str, float] = Field(default_factory=dict)

    # List of column names to be displayed. If empty, all columns are shown.
    visible_columns: list[str] = Field(default_factory=list)

    # List defining the order in which columns should be displayed. If empty, the default order is used.
    column_order: list[str] = Field(default_factory=list)

    # Flag to enable or disable pagination.
    enable_pagination: bool = True

    # Number of rows to display per page when pagination is enabled.
    rows_per_page: int = 20

    # Index of the first row on the current page, used for pagination.
    current_page_start_idx: int = 0

    # List of tuples specifying columns to sort by and the sort order.
    # Each tuple contains a column name and a boolean indicating ascending order.
    sort_by: list[tuple[str, bool]] = Field(default_factory=list)  # (column_name, ascending)

    # Dictionary to define filters for specific columns.
    # Each key is a column name, and the value is another dictionary specifying the condition and value for filtering.
    # Example: {"column_name": {"condition": "value"}}
    # Conditions could be equality, greater than, less than, etc.
    # Example:
    #     filters = {
    #         "age": {"gt": "30"},  # Filter rows where the age column value is greater than 30
    #         "fare": {"lt": "50"},  # Filter rows where the fare column value is less than 50
    #         "name": {"contains": "Smith"}  # Filter rows where the name column contains "Smith"
    #     }
    filters: dict[str, dict[str, str]] = Field(default_factory=dict)

    # Global search term to filter rows based on any column.
    search_query: str = ""

    def validate_params(self, dataframe: pd.DataFrame) -> bool:
        # Validate the params based on the DataFrame
        # Remove any invalid column names from visible_columns, column_order, column_widths, sort_by, and filters
        new_params = copy.copy(self)

        valid_columns = set(dataframe.columns)

        new_params.visible_columns = [col for col in self.visible_columns if col in valid_columns]
        new_params.column_order = [col for col in self.column_order if col in valid_columns]
        new_params.column_widths_em = {}
        for col, width in self.column_widths_em.items():
            if col in valid_columns:
                new_params.column_widths_em[col] = width
        new_params.sort_by = [(col, asc) for col, asc in self.sort_by if col in valid_columns]
        new_params.filters = {col: cond for col, cond in self.filters.items() if col in valid_columns}

        # Use dict() method to convert models to dictionaries for comparison
        changed = new_params.dict() != self.dict()

        if changed:
            self.visible_columns = new_params.visible_columns
            self.column_order = new_params.column_order
            self.column_widths_em = new_params.column_widths_em
            self.sort_by = new_params.sort_by
            self.filters = new_params.filters

        return changed


class DataFramePresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: DataFramePresenterParams

    # A cached version of the DataFrame to present
    # (I'm not sure that we need this cache, since present_custom receives the DataFrame as an argument)
    data_frame: pd.DataFrame

    def __init__(self) -> None:
        self.params = DataFramePresenterParams()

    @staticmethod
    def present_str(value: pd.DataFrame) -> str:
        if value.empty:
            return "DataFrame: Empty"

        num_rows, num_columns = value.shape
        column_info = ", ".join([f"{col} ({dtype})" for col, dtype in zip(value.columns, value.dtypes)])
        memory_usage = value.memory_usage(deep=True).sum()

        return (
            f"DataFrame: {num_rows} rows, {num_columns} columns\n"
            f"Columns: {column_info}\n"
            f"Memory Usage: {memory_usage} bytes"
        )

    def on_change(self, value: pd.DataFrame) -> None:
        # We create a copy because we might change settings in the data frame
        # (ordering, filtering, etc.)
        self.data_frame = copy.copy(value)

    def on_custom_attrs_changed(self, custom_attrs: CustomAttributesDict) -> None:
        # Update the params with the custom attributes
        pass

    def present_custom(self, _value: pd.DataFrame) -> None:
        # We ignore the value parameter since the data frame is cached inside self.data_frame
        if len(self.data_frame.columns) == 0:
            imgui.text("DataFrame: Empty")
            return

        # Compute displayed columns
        displayed_columns: List[str]
        if len(self.params.visible_columns) > 0:
            displayed_columns = self.params.visible_columns
        else:
            displayed_columns = self.data_frame.columns.tolist()  # Convert to list

        # Apply sorting
        sorted_dataframe = self.data_frame
        for col, ascending in reversed(self.params.sort_by):
            sorted_dataframe = sorted_dataframe.sort_values(by=col, ascending=ascending)

        # Calculate pagination
        total_rows = len(sorted_dataframe)
        total_pages = (total_rows + self.params.rows_per_page - 1) // self.params.rows_per_page
        current_page = self.params.current_page_start_idx // self.params.rows_per_page + 1

        # Apply pagination
        start_idx = self.params.current_page_start_idx
        end_idx = start_idx + self.params.rows_per_page
        paginated_dataframe = sorted_dataframe.iloc[start_idx:end_idx]

        # Begin the table
        def show_table():
            # a lambda function to show the table, so that we can pass it to the widget_with_resize_handle
            table_outer_size = hello_imgui.em_to_vec2(*self.params.widget_size_em)
            table_flags = (
                0  # imgui.TableFlags_.resizable.value | imgui.TableFlags_.sortable | imgui.TableFlags_.reorderable ?
            )
            table_inner_width = 0.0  # Use the full width of the table
            if imgui.begin_table(
                str_id="DataFrameTable",
                column=len(displayed_columns),
                flags=table_flags,
                outer_size=table_outer_size,
                inner_width=table_inner_width,
            ):
                # Setup columns
                for col in displayed_columns:
                    column_label = col
                    column_width = self.params.column_widths_em.get(col, 0.0)
                    imgui.table_setup_column(column_label, imgui.TableColumnFlags_.width_fixed.value, column_width)

                # Create headers
                imgui.table_headers_row()

                # Populate rows and cells
                for idx, row in paginated_dataframe.iterrows():
                    imgui.table_next_row()
                    for col in displayed_columns:
                        imgui.table_next_column()
                        imgui.text(str(row[col]))

                # End the table
                imgui.end_table()

        # Draw the table lambda, with a resize handle
        new_table_size_pixels = hello_imgui.widget_with_resize_handle("DataFrameTable", widget_gui_function=show_table)
        # update the widget size in em
        new_table_size_em = hello_imgui.pixels_to_em(new_table_size_pixels)
        self.params.widget_size_em = (new_table_size_em.x, new_table_size_em.y)

        # Add pagination controls
        if total_pages > 1 and self.params.enable_pagination:
            with imgui_ctx.begin_horizontal("DataFramePagination"):
                with fontawesome_6_ctx():
                    page_label = f"{current_page} / {total_pages}"

                    # A spring to align the rest of the controls to the right
                    imgui.spring()

                    # Backward buttons
                    previous_button_enabled = start_idx > 0
                    imgui.begin_disabled(not previous_button_enabled)
                    # first page button
                    if imgui.button(icons_fontawesome_6.ICON_FA_BACKWARD_FAST) and start_idx > 0:
                        self.params.current_page_start_idx = 0
                    # previous page button
                    if imgui.button(icons_fontawesome_6.ICON_FA_BACKWARD) and start_idx > 0:
                        self.params.current_page_start_idx = max(0, start_idx - self.params.rows_per_page)
                    imgui.end_disabled()

                    # Page label
                    imgui.text(page_label)

                    # Forward buttons
                    next_button_enabled = end_idx < total_rows
                    imgui.begin_disabled(not next_button_enabled)
                    if imgui.button(icons_fontawesome_6.ICON_FA_FORWARD) and end_idx < total_rows:
                        self.params.current_page_start_idx = min(
                            total_rows - self.params.rows_per_page, start_idx + self.params.rows_per_page
                        )
                    if imgui.button(icons_fontawesome_6.ICON_FA_FORWARD_FAST) and end_idx < total_rows:
                        self.params.current_page_start_idx = total_rows - self.params.rows_per_page
                    imgui.end_disabled()

    def save_gui_options_to_json(self) -> JsonDict:
        # Here we should save the params to a JSON dict
        return self.params.model_dump(mode="json")

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        # Here we should load params options from a JSON dict
        self.params = DataFramePresenterParams.model_validate(json_dict)
