from abc import ABC

from sswrap.spreadsheet import Spreadsheet


class WritableSpreadsheet(Spreadsheet, ABC):
    def __init__(self):
        super().__init__()

    def add_worksheet(self) -> "WritableWorksheet":
        raise NotImplementedError()
