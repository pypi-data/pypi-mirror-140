from enum import Enum, unique
from typing import List, Union

from .data_grid_type import (
    DataGridType,
    data_grid_types_arg_parser,
    data_grid_type_value_by_content_type,
)
from .._content_provider import ContentProviderLayer
from .._content_type import ContentType
from .._df_build_type import DFBuildType
from ...configure import get_config
from ...core.session import get_valid_session, SessionType
from ...tools import ArgsParser, make_convert_to_enum_arg_parser


@unique
class RowHeaders(Enum):
    DATE = "date"


row_headers_enum_arg_parser = make_convert_to_enum_arg_parser(RowHeaders)


def parse_row_headers(value) -> Union[RowHeaders, List[RowHeaders]]:
    if value is None:
        return []

    value = row_headers_enum_arg_parser.parse(value)

    return value


row_headers_arg_parser = ArgsParser(parse_row_headers)


def get_content_type() -> ContentType:
    from ...delivery.data._data_provider_factory import get_api_config

    config = get_api_config(ContentType.DATA_GRID_RDP, get_config())
    name_platform = config.setdefault("underlying-platform", DataGridType.RDP.value)
    name_platform = data_grid_types_arg_parser.get_str(name_platform)
    content_type = data_grid_type_value_by_content_type.get(name_platform)
    return content_type


def get_layout(row_headers: List[RowHeaders], content_type: ContentType) -> dict:
    layout = None

    is_rdp = content_type is ContentType.DATA_GRID_RDP
    is_udf = content_type is ContentType.DATA_GRID_UDF

    if is_udf:
        layout = {
            "layout": {
                "columns": [{"item": "dataitem"}],
                "rows": [{"item": "instrument"}],
            }
        }
    elif is_rdp:
        layout = {"output": "Col,T|Va,Row,In|"}

    if RowHeaders.DATE in row_headers:
        if is_udf:
            layout["layout"]["rows"].append({"item": "date"})

        elif is_rdp:
            output = layout["output"]
            output = output[:-1]  # delete forward slash "|"
            output = f"{output},date|"
            layout["output"] = output

    else:
        layout = ""

    if layout is None:
        raise ValueError(
            f"Layout is None, row_headers={row_headers}, content_type={content_type}"
        )

    return layout


def get_dfbuild_type(row_headers: List[RowHeaders]) -> DFBuildType:
    dfbuild_type = DFBuildType.INDEX

    if RowHeaders.DATE in row_headers:
        dfbuild_type = DFBuildType.DATE_AS_INDEX

    return dfbuild_type


class DataGridContentProviderLayer(ContentProviderLayer):
    def __init__(
        self,
        content_type: ContentType,
        **kwargs,
    ):
        row_headers = kwargs.get("row_headers")
        row_headers = row_headers_arg_parser.get_list(row_headers)
        layout = get_layout(row_headers, content_type)
        dfbuild_type = get_dfbuild_type(row_headers)
        super().__init__(
            content_type=content_type,
            layout=layout,
            __dfbuild_type__=dfbuild_type,
            **kwargs,
        )

    async def get_data_async(self, session=None, on_response=None, **kwargs):
        """
        Returns a response asynchronously to the data platform

        Parameters
        ----------
        session : Session, optional
            Means default session would be used
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        Response

        Raises
        ------
        AttributeError
            If user didn't set default session.

        """
        from .._content_type import ContentType
        from ...delivery.data._data_provider import emit_event
        from ...delivery.data._data_provider_factory import get_url, get_api_config

        session = get_valid_session(session)
        config = session.config
        if (
            session.type == SessionType.PLATFORM
            and self._content_type == ContentType.DATA_GRID_UDF
        ):
            session.debug(
                f"UDF DataGrid service cannot be used with platform sessions, RDP DataGrid will be used instead. "
                f"The \"/apis/data/datagrid/underlying-platform = '{DataGridType.UDF.value}'\" "
                f"parameter will be discarded, meaning that the regular RDP DataGrid "
                f"service will be used for Fundamental and Reference data requests."
            )
            content_type = self._kwargs["__content_type__"]
            row_headers = kwargs.get("row_headers")
            row_headers = row_headers_arg_parser.get_list(row_headers)
            layout = get_layout(row_headers, content_type)
            dfbuild_type = get_dfbuild_type(row_headers)
            self._kwargs["layout"] = layout
            self._kwargs["__dfbuild_type__"] = dfbuild_type

            self._initialize(ContentType.DATA_GRID_RDP, **self._kwargs)

        data_type = self._data_type
        url = get_url(data_type, config)
        api_config = get_api_config(data_type, config)
        auto_retry = api_config.get("auto-retry", False)
        response = await self._provider.get_data_async(
            session, url, auto_retry=auto_retry, **kwargs, **self._kwargs
        )
        on_response and emit_event(on_response, response, self, session)
        return response
