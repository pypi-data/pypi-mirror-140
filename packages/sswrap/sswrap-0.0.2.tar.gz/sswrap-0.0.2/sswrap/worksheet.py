from abc import ABC, abstractmethod
from typing import List, Any


class Worksheet(ABC):
    @abstractmethod
    def get_value(self, row_index: int, col_index: int) -> Any:
        raise NotImplementedError()
