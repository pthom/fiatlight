from imgui_bundle import imgui
from typing import Generic
from typing import TypeVar

DataType = TypeVar("DataType")
HashId = int


class CachePerImGuiView(Generic[DataType]):
    """A cache that enables to store a value that will differ between ImGui views.
    More precisely, the cache depends on the ImGui ID stack (which varies between views).
    Use this cache to store values that are specific to a view, and that should not be shared between views.
    """

    cache: dict[HashId, DataType]
    default_value: DataType
    str_id: str

    def __init__(self, str_id: str, default_value: DataType) -> None:
        self.cache = {}
        self.str_id = str_id
        self.default_value = default_value

    def get_for_current_view(self) -> DataType:
        """Retrieve the cached value for the current ImGui view, or return the default value."""
        hash_id = imgui.get_id(self.str_id)
        result = self.cache.get(hash_id, self.default_value)
        return result

    def set_for_current_view(self, value: DataType) -> None:
        """Set the cache value for the current ImGui view."""
        hash_id = imgui.get_id(self.str_id)
        self.cache[hash_id] = value

    def set_for_all_views(self, value: DataType) -> None:
        """Set the same value for all views by resetting the cache and updating the default."""

        self.cache.clear()
        self.default_value = value
