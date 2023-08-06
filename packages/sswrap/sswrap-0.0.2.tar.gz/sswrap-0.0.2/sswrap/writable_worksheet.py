from abc import ABC, abstractmethod
from typing import Any, List

from sswrap.worksheet import Worksheet


class WritableWorksheet(Worksheet, ABC):
    @abstractmethod
    def rows(self) -> List[List[Any]]:
        raise NotImplementedError()

    @abstractmethod
    def set_value(self, row_index: int, col_index: int, value: Any):
        raise NotImplementedError()
