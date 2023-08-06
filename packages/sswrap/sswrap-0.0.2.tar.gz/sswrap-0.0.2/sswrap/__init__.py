import csv
import os
from pathlib import Path
from typing import Union

__version__ = "0.0.2"


def load(path: Union[str, Path]) -> "Spreadsheet":
    from .in_memory_spreadsheet import InMemorySpreadsheet
    from .spreadsheet import Spreadsheet
    from .writable_spreadsheet import WritableSpreadsheet
    from .writable_worksheet import WritableWorksheet
    if isinstance(path, str) and os.path.exists(path):
        path = Path(path)

    if isinstance(path, Path) and path.suffix == ".csv":
        ss: WritableSpreadsheet = InMemorySpreadsheet()
        ws: WritableWorksheet = ss.add_worksheet()
        rows = ws.rows
        assert len(rows) == 0
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        return ss
    raise NotImplementedError(f"\"{path}\" is not supported yet")
