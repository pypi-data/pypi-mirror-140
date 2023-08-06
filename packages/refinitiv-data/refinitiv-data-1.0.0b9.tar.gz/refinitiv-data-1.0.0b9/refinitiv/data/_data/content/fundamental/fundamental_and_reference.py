# coding: utf8

__all__ = ["Definition"]

from typing import TYPE_CHECKING, Union, List

from ._data_grid_provider_layer import (
    DataGridContentProviderLayer,
    get_content_type,
    RowHeaders,
)
from ...tools import create_repr

if TYPE_CHECKING:
    from .._types import ExtendedParams, OptBool, OptDict


class Definition(DataGridContentProviderLayer):
    """
    This class describe the universe (list of instruments), the fields
    (a.k.a. data items) and parameters that will be requested to the data platform

    Parameters:
    ----------
    universe : str or list of str
        The list of RICs
    fields : str or list of str
        List of fundamental field names
    parameters : dict, optional
        Global parameters for fields
    row_headers : str, list of str, list of RowHeaders enum
        When this parameter is used, the output/layout parameter will be added
        to the underlying request to DataGrid RDP or UDF
    use_field_names_in_headers : bool, optional
        If value is True we add field names in headers.
    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
     >>> from refinitiv.data.content import fundamental_and_reference
     >>> definition = fundamental_and_reference.Definition(["IBM"], ["TR.Volume"])
     >>> definition.get_data()

     Using get_data_async
     >>> import asyncio
     >>> task = asyncio.gather(
     ...    definition.get_data_async(),
     ...)
     >>> asyncio.get_event_loop().run_until_complete(task)
     >>> response, *_ = task.result()
    """

    def __init__(
        self,
        universe: Union[str, List[str]],
        fields: Union[str, List[str]],
        parameters: "OptDict" = None,
        row_headers: Union[str, List[str], List[RowHeaders]] = None,
        use_field_names_in_headers: "OptBool" = False,
        extended_params: "ExtendedParams" = None,
    ):
        self.universe = universe
        self.fields = fields
        self.parameters = parameters
        self.use_field_names_in_headers = use_field_names_in_headers
        self.extended_params = extended_params
        self.row_headers = row_headers
        content_type = get_content_type()
        super().__init__(
            content_type=content_type,
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            row_headers=self.row_headers,
            use_field_names_in_headers=self.use_field_names_in_headers,
            extended_params=self.extended_params,
        )

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.fundamental_and_reference",
            content=f"{{"
            f"universe='{self.universe}', "
            f"fields='{self.fields}', "
            f"parameters='{self.parameters}', "
            f"row_headers='{self.row_headers}'"
            f"}}",
        )
