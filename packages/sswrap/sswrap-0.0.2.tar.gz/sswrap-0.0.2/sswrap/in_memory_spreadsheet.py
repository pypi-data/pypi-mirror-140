from typing import List

from sswrap.in_memory_worksheet import InMemoryWorksheet
from sswrap.worksheet import Worksheet
from sswrap.writable_spreadsheet import WritableSpreadsheet
from sswrap.writable_worksheet import WritableWorksheet


class InMemorySpreadsheet(WritableSpreadsheet):
    """\
    A spreadsheet implementation that contains all data in memory (mere lists!)
    In fact this may not be called a "spreadsheet" but just a list of in-memory table data.
    """
    def __init__(self):
        self._worksheets: List[Worksheet] = []

    def num_worksheets(self) -> int:
        return len(self._worksheets)

    def add_worksheet(self) -> "WritableWorksheet":
        ws = InMemoryWorksheet()
        self._worksheets.append(ws)
        return ws

    def __getitem__(self, index: int) -> "Worksheet":
        return self._worksheets[index]

    def __len__(self) -> int:
        return len(self._worksheets)
