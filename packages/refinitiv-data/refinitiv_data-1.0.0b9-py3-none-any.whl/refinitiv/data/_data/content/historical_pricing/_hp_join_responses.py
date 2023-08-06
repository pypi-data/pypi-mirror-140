from types import SimpleNamespace
from typing import List, Tuple, TYPE_CHECKING, Callable

import numpy as np
import pandas as pd
from pandas import DataFrame

from ...delivery.data._data_provider import Data, Response
from .._join_responses import join_dfs

from ...errors import RDError

if TYPE_CHECKING:
    from ._hp_data_provider import DayIntervalType


def get_response(fields: List[str], responses: List[Tuple[str, Response]]) -> Response:
    inst_name, response = responses[0]
    df = response.data.df
    if df is not None:
        df = create_df_with_not_valid_fields(fields, df) if fields else df
        df.axes[1].name = inst_name
        response.data = Data(response.data.raw, df)
    return response


def create_df_with_not_valid_fields(fields: List[str], df: DataFrame) -> DataFrame:
    not_valid_columns = set(fields) - set(df.columns.values)
    new_df = df.assign(**{column_name: np.NaN for column_name in not_valid_columns})
    return new_df


def get_fields(**kwargs) -> list:
    fields = kwargs.get("fields")
    if not (fields is None or isinstance(fields, list)):
        raise AttributeError(f"fields not support type {type(fields)}")

    fields = fields or []
    return fields[:]


def join_responses_hp_summaries(get_data_async: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Response:
        from ._hp_data_provider import axis_by_day_interval_type

        fields = get_fields(**kwargs)
        responses: List[Tuple[str, Response]] = await get_data_async(*args, **kwargs)

        if len(responses) == 1:
            _, _response = responses[0]
            if not _response.is_success:
                return _response
            get_first_successful_df(responses)
            response = get_response(fields, responses)
            response.data.df.index.name = "Date"
            return response

        day_interval_type: "DayIntervalType" = kwargs.get("day_interval_type")
        axis_name = axis_by_day_interval_type.get(day_interval_type)
        return join_responses(fields, responses, new_axis_name=axis_name)

    return wrapper


def join_responses_hp_events(get_data_async: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Response:
        fields = get_fields(**kwargs)
        responses: List[Tuple[str, Response]] = await get_data_async(*args, **kwargs)

        if len(responses) == 1:
            _, _response = responses[0]

            if not _response.is_success:
                return _response
            get_first_successful_df(responses)
            response = get_response(fields, responses)
            response.data.df.index.name = "Timestamp"
            return response

        return join_responses(fields, responses, new_axis_name="Timestamp")

    return wrapper


def is_success_response(response: Response) -> bool:
    return response.is_success and response.data.df is not None


def get_first_successful_df(responses: List[Tuple[str, Response]]) -> DataFrame:
    successful = (
        response.data.df for _, response in responses if is_success_response(response)
    )
    first_successful_df = next(successful, None)

    if first_successful_df is None:
        error_message = "ERROR: No successful response.\n"
        for inst_name, response in responses:
            _error_message = None
            if response.errors:
                _error_message = response.errors[0].message
            error_message += "({error_code}, {error_message}), ".format(
                error_code=response.errors[0].code,
                error_message=response.errors[0].message,
            )
        error_message = error_message[:-2]
        raise RDError(1, f"No data to return, please check errors: {error_message}")
    return first_successful_df


def join_responses(
    fields: List[str], responses: List[Tuple[str, Response]], new_axis_name: str
) -> Response:
    first_successful_df = get_first_successful_df(responses)

    raws = []
    errors = []
    http_statuses = []
    http_headers = []
    http_responses = []
    request_messages = []

    columns = (None,)
    dfs = []
    for inst_name, response in responses:
        raws.append(response.data.raw)
        http_statuses.append(response.http_status)
        http_headers.append(response.http_headers)
        request_messages.append(response.request_message)
        http_responses.append(response.http_response)
        if response.errors:
            errors += response.errors

        df = response.data.df
        if fields and is_success_response(response):
            df = create_df_with_not_valid_fields(fields, df)
        elif fields and df is None:
            df = DataFrame(columns=fields, index=first_successful_df.index.to_numpy())
        elif df is None:
            df = DataFrame(columns=columns, index=first_successful_df.index.to_numpy())

        df.columns = pd.MultiIndex.from_product([[inst_name], df.columns])
        dfs.append(df)
    raw_response = SimpleNamespace()
    raw_response.request = SimpleNamespace()
    # dfs = [df for df in dfs if df is not None]
    df = join_dfs(dfs, how="outer")

    if not df.empty:
        df = df.rename_axis(new_axis_name)
    raw_response.request = request_messages
    raw_response.headers = http_headers
    response = Response(raw_response=raw_response, is_success=True)
    response.errors += errors
    response.data = Data(raws, dataframe=df)
    response._status = http_statuses
    response.http_response = http_responses

    return response
