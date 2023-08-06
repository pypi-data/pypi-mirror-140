import os.path
from enum import Enum
from typing import List, Any, Dict, Optional

import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from sswrap.common import to_a1_range, from_a1_cell
from sswrap.exceptions import SswrapException
from sswrap.spreadsheet import Spreadsheet
from sswrap.worksheet import Worksheet

_DEFAULT_CREDENTIAL_PATH = "credentials.json"
_DEFAULT_TOKEN_PATH = "token.json"
_DEFAULT_WRITABLE = False
_DEFAULT_PREFETCH = True


def _prepare_spreadsheets_resource(*,
                                   credential_path: str = _DEFAULT_CREDENTIAL_PATH,
                                   token_path: str = _DEFAULT_TOKEN_PATH,
                                   writable: bool = _DEFAULT_WRITABLE) -> googleapiclient.discovery.Resource:
    """\
    Constructs a googleapiclient.discovery.Resource for interacting with Google Sheets API.

    See https://developers.google.com/sheets/api/reference/rest

    :param credential_path:
    :param token_path:
    :param writable:
    :return: Resource object for interacting with Google Sheets API
    """
    scopes: List[str]
    if writable:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    else:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # Based on https://developers.google.com/sheets/api/quickstart/python
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credential_path, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    if not creds:
        raise SswrapException("Failed to create a credential for Google Sheets API")
    return build("sheets", "v4", credentials=creds).spreadsheets()


class ValueRenderOption(Enum):
    """\
    See also https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    """
    # Values will be calculated & formatted in the reply according to the cell's formatting.
    # Formatting is based on the spreadsheet's locale, not the requesting user's locale.
    # For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "$1.23".
    FORMATTED_VALUE = "FORMATTED_VALUE"

    # Values will be calculated, but not formatted in the reply.
    # For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return the number 1.23.
    UNFORMATTED_VALUE = "UNFORMATTED_VALUE"

    # Values will not be calculated. The reply will include the formulas.
    # For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "=A1".
    FORMULA = "FORMULA"

    def __str__(self):
        return self.value


class GoogleSpreadsheet(Spreadsheet):
    def __init__(self,
                 spreadsheet_id: str,
                 *,
                 credential_path: str = _DEFAULT_CREDENTIAL_PATH,
                 token_path: str = _DEFAULT_TOKEN_PATH,
                 writable: bool = _DEFAULT_WRITABLE,
                 value_render_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE):
        super().__init__()
        self._spreadsheet_id = spreadsheet_id
        self._resource = _prepare_spreadsheets_resource(credential_path=credential_path,
                                                        token_path=token_path,
                                                        writable=writable)
        self._metadata = self._get_remote_metadata()
        self._value_render_option = value_render_option

    @property
    def metadata(self):
        return self._metadata

    def _get_remote_metadata(self):
        return self._resource.get(spreadsheetId=self._spreadsheet_id, fields=None).execute()

    def num_worksheets(self) -> int:
        return len(self._metadata.get('sheets', 0))

    def __getitem__(self, index: int) -> "GoogleWorksheet":
        return GoogleWorksheet(self,
                               self._metadata.get('sheets', [])[index],
                               value_render_option=self._value_render_option)

    def __len__(self) -> int:
        return len(self._metadata.get('sheets', []))


class GoogleWorksheet(Worksheet):
    def __init__(self,
                 spreadsheet: "GoogleSpreadsheet",
                 metadata: Dict[str, Any],
                 *,
                 value_render_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE):
        self._spreadsheet = spreadsheet
        self._metadata = metadata
        grid_properties = self._metadata["properties"]["gridProperties"]
        row_count = grid_properties["rowCount"]
        col_count = grid_properties["columnCount"]
        # TODO: Implement non-cache initialization
        self._cache: Optional[List[List[Any]]] = self._get_remote_range(
            0, 0, row_count - 1, col_count - 1, value_render_option=value_render_option)

    @property
    def title(self):
        return self._metadata["properties"]["title"]

    def _get_remote_range(self,
                          start_row_index: int,
                          start_col_index: int,
                          end_row_index: int,
                          end_col_index: int,
                          *,
                          value_render_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE)\
            -> List[List[Any]]:
        range_str = to_a1_range(start_row_index, start_col_index, end_row_index, end_col_index)
        result = self._spreadsheet._resource.values().get(spreadsheetId=self._spreadsheet._spreadsheet_id,
                                                          range="{}!{}".format(self.title, range_str),
                                                          valueRenderOption=value_render_option.value).execute()
        return result.get('values')

    def get_value(self, row_index: int, col_index: int) -> Any:
        return self._cache[row_index][col_index]

    def get_by_cell(self, cell: str) -> Any:
        row_index, col_index = from_a1_cell(cell)
        return self.get_value(row_index, col_index)


def _run_smoke_test():
    """\
    Runs a simple procedure demonstrating Google Sheets API.
    See also https://developers.google.com/sheets/api/quickstart/python
    """
    resource = _prepare_spreadsheets_resource()
    # This spreadsheet is maintained by Google, not by us.
    result = resource.values().get(spreadsheetId="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                                   range="Class Data!A2:E").execute()
    values = result.get("values", [])

    if not values:
        print("No data found.")
        return

    print("Name, Major:")
    for row in values:
        # Print columns A and E, which correspond to indices 0 and 4.
        print(f"{row[0]}, {row[4]}")


if __name__ == "__main__":
    print("Start running an embedded smoke test")
    _run_smoke_test()
