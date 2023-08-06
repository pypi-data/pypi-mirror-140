import string
from typing import Tuple

from sswrap.exceptions import SswrapException


def to_a1_cell(row_index: int, col_index: int) -> str:
    lst = []
    # 0 .. A, 25 .. Z, 26 .. AA, 51 .. AZ, 52 ... BA
    while col_index > 25:
        lst.append(string.ascii_uppercase[col_index % 26])
        col_index = (col_index // 26) - 1
    lst.append(string.ascii_uppercase[col_index % 26])
    return "{}{}".format("".join(reversed(lst)), row_index + 1)


def to_a1_range(start_row_index: int, start_col_index: int, end_row_index: int, end_col_index: int) -> str:
    return "{}:{}".format(to_a1_cell(start_row_index, start_col_index),
                          to_a1_cell(end_row_index, end_col_index))


def from_column_str(col_str: str) -> int:
    total = 0
    for i, ch in enumerate(reversed(col_str.upper())):
        total += (ord(ch) - 64) * (26 ** i)
    return total - 1


def from_a1_cell(cell: str) -> Tuple[int, int]:
    for i, ch in enumerate(cell):
        if ch in string.ascii_uppercase:
            continue
        elif ch in string.digits:
            break
        else:
            raise SswrapException(f"Unexpected character \"{ch}\" found")
    return int(cell[i:]) - 1, from_column_str(cell[:i])
