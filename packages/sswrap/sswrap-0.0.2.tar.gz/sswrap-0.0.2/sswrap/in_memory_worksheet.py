from typing import List, Any

from sswrap.writable_worksheet import WritableWorksheet


class InMemoryWorksheet(WritableWorksheet):
    def __init__(self):
        self._rows: List[List[Any]] = []

    @property
    def rows(self) -> List[List[Any]]:
        return self._rows

    def set_value(self, row_index: int, col_index: int, value: Any):
        self._rows[row_index][col_index] = value

    def get_value(self, row_index: int, col_index: int) -> Any:
        return self._rows[row_index][col_index]
