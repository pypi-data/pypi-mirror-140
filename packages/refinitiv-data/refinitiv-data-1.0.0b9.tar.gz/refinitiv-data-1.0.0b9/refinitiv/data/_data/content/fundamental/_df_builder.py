from typing import List, Optional

import numpy as np
import pandas as pd


def set_date_as_index(
    content_headers: List[dict],
    df: pd.DataFrame,
    use_field_names_in_headers: bool,
    auto_headers: List[dict],
) -> pd.DataFrame:
    inst_header = auto_headers[0]
    date_header = auto_headers[1]

    if use_field_names_in_headers:
        key = "name"
    else:
        key = "title"

    auto_headers = [inst_header[key], date_header[key]]
    inst_header = inst_header[key]
    date_header = date_header[key]
    shift = len(auto_headers)

    if len(content_headers) < shift:
        return df

    # check if automatic headers are in dataframe as first 2 columns
    content_headers_set = set([header[key] for header in content_headers[:shift]])
    auto_headers_set = set(auto_headers)
    if auto_headers_set != content_headers_set:
        return df

    add_suffix = False
    content_headers = [header[key] for header in content_headers]
    # Detect if automatic_header names are duplicated in indexes
    for auto_header in auto_headers:
        # detect if automatic header is duplicated in other columns,
        # then replace other column title with full name
        if content_headers.count(auto_header) > 1:
            add_suffix = True

            headers_without_auto_headers = content_headers[shift:]
            for idx, header in enumerate(headers_without_auto_headers):

                if header == auto_header:
                    idx_shift = idx + shift
                    old_header = content_headers[idx_shift]
                    new_header = f"{old_header}._{idx}"
                    content_headers[idx_shift] = new_header

            df.columns = content_headers

    result = None
    insts = df[inst_header]
    proc_insts = set()
    num_unique_insts = len(set(insts))

    # Iterate by Series to save iteration order
    for inst_name in insts:

        if inst_name in proc_insts:
            continue

        proc_insts.add(inst_name)

        inst_df = df[insts == inst_name]
        inst_df = inst_df.drop(inst_header, axis=1)

        if num_unique_insts > 1:
            columns = [(date_header,)]
            columns.extend(
                [
                    (inst_name, header)
                    for header in inst_df.columns
                    if header != date_header
                ]
            )
            inst_df.columns = pd.MultiIndex.from_tuples(columns)

        else:
            inst_df.axes[1].name = inst_name

        if result is None:
            result = inst_df

        else:
            result = pd.merge(result, inst_df, how="outer")

    result.set_index(result.columns[0], inplace=True)
    result.index.rename(date_header, inplace=True)

    if add_suffix:
        if isinstance(result.columns, pd.MultiIndex):
            level = 1
            columns = result.columns.levels[level]

        else:
            level = 0
            columns = result.columns

        new_columns = []

        for column in columns:

            if "._" in column:
                column, *_ = column.split("._")

            new_columns.append(column)

        new_columns = dict(zip(columns, new_columns))
        result = result.rename(columns=new_columns, level=level)

    result.index = pd.to_datetime(result.index, utc=True)

    nats = []
    for idx in result.index:
        if pd.isna(idx):
            nats.append(idx)

    result.drop(nats, inplace=True)
    result.sort_index(ascending=False, inplace=True)
    result.fillna(pd.NA, inplace=True)

    return result


class DFBuilder:
    auto_headers: Optional[List] = None

    def __init__(self) -> None:
        self.headers = None

    def get_headers(self, content_data):
        return []

    def get_date_header(self):
        return ""

    def build_index(
        self, content_data: dict, use_field_names_in_headers: bool = False
    ) -> pd.DataFrame:

        if "headers" not in content_data or "data" not in content_data:
            self.headers = []
            return pd.DataFrame()

        if use_field_names_in_headers:
            key = "name"
        else:
            key = "title"

        self.headers = self.get_headers(content_data)
        columns = [header[key] for header in self.headers]

        data = content_data["data"]
        data = np.array(data)
        df = pd.DataFrame(data, columns=columns)
        df.fillna(pd.NA, inplace=True)
        df = df.convert_dtypes()
        return df

    def build_date_as_index(
        self, content_data: dict, use_field_names_in_headers: bool = False
    ) -> pd.DataFrame:
        df = self.build_index(content_data, use_field_names_in_headers)
        df = set_date_as_index(
            self.headers, df, use_field_names_in_headers, self.auto_headers
        )
        return df


class DFBuilderRDP(DFBuilder):
    """
    {
        "links": {"count": 2},
        "variability": "",
        "universe": [
            {
                "Instrument": "GOOG.O",
                "Company Common Name": "Alphabet Inc",
                "Organization PermID": "5030853586",
                "Reporting Currency": "USD",
            }
        ],
        "data": [
            ["GOOG.O", "2022-01-26T00:00:00", "USD", None],
            ["GOOG.O", "2020-12-31T00:00:00", None, "2020-12-31T00:00:00"],
        ],
        "messages": {
            "codes": [[-1, -1, -1, -2], [-1, -1, -2, -1]],
            "descriptions": [
                {"code": -2, "description": "empty"},
                {"code": -1, "description": "ok"},
            ],
        },
        "headers": [
            {
                "name": "instrument",
                "title": "Instrument",
                "type": "string",
                "description": "The requested Instrument as defined by the user.",
            },
            {
                "name": "date",
                "title": "Date",
                "type": "datetime",
                "description": "Date associated with the returned data.",
            },
            {
                "name": "TR.RevenueMean",
                "title": "Currency",
                "type": "string",
                "description": "The statistical average of all broker ...",
            },
            {
                "name": "TR.Revenue",
                "title": "Date",
                "type": "datetime",
                "description": "Is used for industrial and utility companies. ...",
            },
        ],
    }
    """

    auto_headers = [
        {"name": "instrument", "title": "Instrument"},
        {"name": "date", "title": "Date"},
    ]

    def get_headers(self, content_data):
        return content_data["headers"]

    def get_date_header(self):
        return "date"


class DFBuilderUDF(DFBuilder):
    """
    {
        "columnHeadersCount": 1,
        "data": [
            ["GOOG.O", "2022-01-26T00:00:00Z", "USD", ""],
            ["GOOG.O", "2020-12-31T00:00:00Z", "", "2020-12-31T00:00:00Z"],
        ],
        "headerOrientation": "horizontal",
        "headers": [
            [
                {"displayName": "Instrument"},
                {"displayName": "Date"},
                {"displayName": "Currency", "field": "TR.REVENUEMEAN.currency"},
                {"displayName": "Date", "field": "TR.REVENUE.DATE"},
            ]
        ],
        "rowHeadersCount": 2,
        "totalColumnsCount": 4,
        "totalRowsCount": 3,
    }
    """

    auto_headers = [
        {"name": "Instrument", "title": "Instrument"},
        {"name": "Date", "title": "Date"},
    ]

    def get_headers(self, content_data):
        headers_data = content_data["headers"]
        headers_data = headers_data[0]
        return [
            {
                "name": header.get("field") or header.get("displayName"),
                "title": header.get("displayName"),
            }
            for header in headers_data
        ]

    def get_date_header(self):
        return "Date"


dfbuilder_rdp = DFBuilderRDP()
dfbuilder_udf = DFBuilderUDF()
