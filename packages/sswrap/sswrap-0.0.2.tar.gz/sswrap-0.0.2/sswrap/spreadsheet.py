from abc import ABC, abstractmethod

from sswrap.worksheet import Worksheet


class Spreadsheet(ABC):
    """\
    A spreadsheet that contains one or multiple worksheets.
    Note that a spreadsheet built from a CSV file just contains a single worksheet, while
    one from an Excel or Google Sheets can contain multiple worksheets.
    """

    @abstractmethod
    def num_worksheets(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, index: int) -> Worksheet:
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()


