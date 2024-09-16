import copy

from pydantic import BaseModel, Field
import pandas as pd
from fiatlight.fiat_core.possible_fiat_attributes import PossibleFiatAttributes
from fiatlight.fiat_types import FiatAttributes, JsonDict
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx, icons_fontawesome_6
from imgui_bundle import imgui, imgui_ctx, hello_imgui, immapp
from fiatlight.fiat_utils.str_utils import memory_readable_str
from fiatlight.fiat_utils import is_rendering_in_node


class DataFramePossibleFiatAttributes(PossibleFiatAttributes):
    # Here we will add all the possible fiat attributes for the DataFrame
    # so that the user can customize the presentation of the DataFrame
    # (probably by settings params in DataFramePresenterParams)
    def __init__(self) -> None:
        super().__init__("DataFrameWithGui")

        self.add_explained_attribute(
            name="widget_size_em",
            explanation="Widget size in em units",
            type_=tuple,
            default_value=(50.0, 15.0),
            tuple_types=(float, float),
        )
        self.add_explained_attribute(
            name="column_widths_em",
            explanation="Dictionary to specify custom widths for individual columns, identified by column name",
            type_=dict,
            default_value={},
            dict_types=(str, float),
        )
        self.add_explained_attribute(
            name="rows_per_page_node",
            explanation="Number of rows to display per page (when displayed in a function node)",
            type_=int,
            default_value=10,
        )
        self.add_explained_attribute(
            name="rows_per_page_classic",
            explanation="Number of rows to display per page (when displayed in a pop-up)",
            type_=int,
            default_value=20,
        )
        self.add_explained_attribute(
            name="current_page_start_idx",
            explanation="Index of the first row on the current page, used for pagination",
            type_=int,
            default_value=0,
        )


_DATAFRAME_POSSIBLE_FIAT_ATTRIBUTES = DataFramePossibleFiatAttributes()


class DataFramePresenterParams(BaseModel):
    # Widget size in em
    widget_size_em: tuple[float, float] = (50.0, 15.0)

    # Dictionary to specify custom widths for individual columns, identified by column name.
    column_widths_em: dict[str, float] = Field(default_factory=dict)

    # List of column names to be displayed. If empty, all columns are shown.
    # Postponed/disabled
    # visible_columns: list[str] = Field(default_factory=list)

    # List defining the order in which columns should be displayed. If empty, the default order is used.
    # Postponed/disabled: ImGui does not seem to communicate back this info after reordering columns.
    # column_order: list[str] = Field(default_factory=list)

    # Number of rows to display per page (when displayed in a function node)
    rows_per_page_node: int = 10
    # Number of rows to display per page (when displayed elsewhere)
    rows_per_page_classic: int = 20

    # Index of the first row on the current page, used for pagination.
    current_page_start_idx: int = 0

    # List of tuples specifying columns to sort by and the sort order.
    # Each tuple contains a column name and a boolean indicating ascending order.
    sort_by: list[tuple[str, bool]] = Field(default_factory=list)  # (column_name, ascending)

    def validate_params(self, dataframe: pd.DataFrame) -> bool:
        # Validate the params based on the DataFrame
        # Remove any invalid column names from visible_columns, column_order, column_widths, sort_by, and filters
        new_params = copy.copy(self)

        valid_columns = set(dataframe.columns)

        # new_params.visible_columns = [col for col in self.visible_columns if col in valid_columns]
        # new_params.column_order = [col for col in self.column_order if col in valid_columns]
        new_params.column_widths_em = {}
        for col, width in self.column_widths_em.items():
            if col in valid_columns:
                new_params.column_widths_em[col] = width
        new_params.sort_by = [(col, asc) for col, asc in self.sort_by if col in valid_columns]

        # Use dict() method to convert models to dictionaries for comparison
        changed = new_params.model_dump() != self.model_dump()

        if changed:
            # self.visible_columns = new_params.visible_columns
            # self.column_order = new_params.column_order
            self.column_widths_em = new_params.column_widths_em
            self.sort_by = new_params.sort_by

        return changed

    @property
    def rows_per_page(self) -> int:
        return self.rows_per_page_node if is_rendering_in_node() else self.rows_per_page_classic

    # setter for rows_per_page
    @rows_per_page.setter
    def rows_per_page(self, value: int) -> None:
        if is_rendering_in_node():
            self.rows_per_page_node = value
        else:
            self.rows_per_page_classic = value


class DataFramePresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: DataFramePresenterParams

    # A cached version of the DataFrame to present
    # (I'm not sure that we need this cache, since present receives the DataFrame as an argument)
    dataframe: pd.DataFrame
    dataframe_original: pd.DataFrame  # unsorted, unfiltered, etc.

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
            f"DataFrame: {num_rows} rows, {num_columns} cols\n"
            f"Columns: {column_info}\n"
            f"Memory Usage: {memory_readable_str(memory_usage)}"
        )

    def on_change(self, value: pd.DataFrame) -> None:
        # Remember the original data frame (this one won't be modified)
        self.dataframe_original = value
        # We create a copy because we might change settings in the data frame (ordering, filtering, etc.)
        self.dataframe = copy.copy(self.dataframe_original)

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        # Update the params with the fiat attributes
        for key, value in fiat_attrs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)

    def _paginated_dataframe(self) -> pd.DataFrame:
        if self.params.current_page_start_idx > len(self.dataframe):
            self.params.current_page_start_idx = 0
        start_idx = self.params.current_page_start_idx
        end_idx = start_idx + self.params.rows_per_page
        paginated_dataframe = self.dataframe.iloc[start_idx:end_idx]
        return paginated_dataframe

    # Add pagination controls
    def _show_pagination_controls(self) -> None:
        # Calculate pagination
        total_rows = len(self.dataframe)
        total_pages = (total_rows + self.params.rows_per_page - 1) // self.params.rows_per_page
        current_page = self.params.current_page_start_idx // self.params.rows_per_page + 1

        start_idx = self.params.current_page_start_idx
        end_idx = start_idx + self.params.rows_per_page

        if True:  # total_pages > 1:
            with imgui_ctx.begin_horizontal("DataFramePagination"):
                with fontawesome_6_ctx():
                    page_label = f"{current_page} / {total_pages}"

                    imgui.push_item_flag(imgui.ItemFlags_.button_repeat.value, True)

                    # Backward buttons
                    previous_button_enabled = start_idx > 0
                    imgui.begin_disabled(not previous_button_enabled)
                    # first page button
                    if imgui.button(icons_fontawesome_6.ICON_FA_BACKWARD_FAST) and start_idx > 0:
                        self.params.current_page_start_idx = 0
                    # previous page button
                    if imgui.button(icons_fontawesome_6.ICON_FA_CARET_LEFT) and start_idx > 0:
                        self.params.current_page_start_idx = max(0, start_idx - self.params.rows_per_page)
                    imgui.end_disabled()

                    # Page label
                    imgui.text(page_label)

                    # Forward buttons
                    next_button_enabled = end_idx < total_rows
                    imgui.begin_disabled(not next_button_enabled)
                    if imgui.button(icons_fontawesome_6.ICON_FA_CARET_RIGHT) and end_idx < total_rows:
                        self.params.current_page_start_idx = min(
                            total_rows - self.params.rows_per_page, start_idx + self.params.rows_per_page
                        )
                    if imgui.button(icons_fontawesome_6.ICON_FA_FORWARD_FAST) and end_idx < total_rows:
                        self.params.current_page_start_idx = total_rows - self.params.rows_per_page
                    imgui.end_disabled()

                    # Info
                    def info_string() -> str:
                        num_rows, num_columns = self.dataframe.shape
                        memory_usage = memory_readable_str(self.dataframe.memory_usage(deep=True).sum())
                        return f"{num_rows} rows, {num_columns} cols, Memory: {memory_usage}"

                    imgui.spring()
                    imgui.text(info_string())

                    # Rows per page
                    imgui.spring()
                    imgui.text("Rows per page:")
                    imgui.set_next_item_width(hello_imgui.em_size(6.0))
                    _, self.params.rows_per_page = imgui.slider_int("##Rows per page", self.params.rows_per_page, 5, 70)

                    imgui.pop_item_flag()

    def _handle_table_sorting(self) -> None:
        # Get the sort specs
        sort_specs = imgui.table_get_sort_specs()
        displayed_columns = self.dataframe.columns.tolist()
        if sort_specs is not None:
            if sort_specs.specs_dirty:
                # Update the sort order
                sort_order = []
                for spec_idx in range(sort_specs.specs_count):
                    spec = sort_specs.get_specs(spec_idx)
                    col_name = displayed_columns[spec.column_index]
                    ascending = spec.get_sort_direction() == imgui.SortDirection.ascending
                    no_sort = spec.get_sort_direction() == imgui.SortDirection.none
                    if not no_sort:
                        sort_order.append((col_name, ascending))
                self.params.sort_by = sort_order

                # Sort the dataframe
                if len(sort_order) > 0:
                    self.dataframe.sort_values(
                        by=[col for col, _ in sort_order], ascending=[asc for _, asc in sort_order], inplace=True
                    )
                else:
                    # go back to the original order
                    self.dataframe = copy.copy(self.dataframe_original)

                sort_specs.specs_dirty = False

    def _show_table(self) -> None:
        displayed_columns = self.dataframe.columns.tolist()

        # a lambda function to show the table, so that we can pass it to the widget_with_resize_handle
        table_outer_size = hello_imgui.em_to_vec2(*self.params.widget_size_em)
        table_flags = (
            imgui.TableFlags_.resizable.value
            | imgui.TableFlags_.hideable.value
            | imgui.TableFlags_.context_menu_in_body.value
            | imgui.TableFlags_.row_bg.value
            | imgui.TableFlags_.sort_multi.value  # can sort on multiple columns
            | imgui.TableFlags_.sort_tristate.value  # can come back to no sort
            | imgui.TableFlags_.sortable.value
        )
        # | imgui.TableFlags_.sortable | imgui.TableFlags_.reorderable.value
        table_inner_width = 0.0  # Use the full width of the table
        if imgui.begin_table(
            str_id="DataFrameTable",
            columns=len(displayed_columns),
            flags=table_flags,
            outer_size=table_outer_size,
            inner_width=table_inner_width,
        ):
            # Setup columns
            for col in displayed_columns:
                column_label = col
                column_width_em = self.params.column_widths_em.get(col, 0.0)
                column_width = hello_imgui.em_size(column_width_em)

                column_flags = 0
                column_flags |= imgui.TableColumnFlags_.width_fixed.value

                imgui.table_setup_column(column_label, column_flags, column_width)

            # Create headers
            imgui.table_headers_row()

            # Populate rows and cells
            paginated_dataframe = self._paginated_dataframe()
            for idx, row in paginated_dataframe.iterrows():
                imgui.table_next_row()
                for col in displayed_columns:
                    imgui.table_next_column()
                    imgui.text(str(row[col]))

            # Extract column order and sizes from the ImGui Table, and save them to params
            # column_order = []
            column_widths_em = {}
            for column_index in range(len(displayed_columns)):
                imgui.table_set_column_index(column_index)
                column_name = imgui.table_get_column_name(column_index)
                column_width = imgui.get_column_width(column_index)
                # column_order.append(column_name)
                column_widths_em[column_name] = hello_imgui.pixel_size_to_em(column_width)
            # Save the extracted order and sizes to params
            # self.params.column_order = column_order
            self.params.column_widths_em = column_widths_em
            # logging.warning(f"column_order: {column_order}")

            # Handle sorting
            self._handle_table_sorting()

            # End the table
            imgui.end_table()

            # if imgui.is_item_hovered():
            #     ed.disable_user_input_this_frame()

    def _show_resizable_table(self) -> None:
        # Draw the table lambda, with a resize handle
        new_table_size_em = immapp.widget_with_resize_handle_in_node_editor_em(  # type: ignore  #  noqa
            "DataFrameTable", self._show_table, resize_handle_size_em=1.5
        )
        self.params.widget_size_em = (new_table_size_em.x, hello_imgui.em_size(1.0))  # new_table_size_em.y)

    def present(self, _value: pd.DataFrame) -> None:
        # We ignore the value parameter since the data frame is cached inside self.dataframe
        if len(self.dataframe.columns) == 0:
            imgui.text("DataFrame: Empty")
            return

        self._show_pagination_controls()
        self._show_resizable_table()

    def save_gui_options_to_json(self) -> JsonDict:
        # Here we should save the params to a JSON dict
        return self.params.model_dump(mode="json")

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        # Here we should load params options from a JSON dict
        self.params = DataFramePresenterParams.model_validate(json_dict)

    def clipboard_copy_str(self, _value: pd.DataFrame) -> str:
        # We ignore the value parameter since the data frame is cached inside self.dataframe
        # (and potentially reordered by the user)
        return self.dataframe.to_csv(index=False, sep="\t")
