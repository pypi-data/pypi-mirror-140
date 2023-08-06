from ._enums import Package
from .._content_provider import (
    ESGAndEstimatesContentValidator,
    ESGAndEstimateParser,
)
from ...delivery.data._data_provider import (
    Data,
    DataProvider,
    RequestFactory,
    ResponseFactory,
)
from ...tools import (
    convert_content_data_to_df,
    universe_arg_parser,
    make_enum_arg_parser,
)


class EstimatesData(Data):
    def __init__(self, raw, use_field_names_in_headers: bool = False, *args, **kwargs):
        super().__init__(raw)
        self._build_df = convert_content_data_to_df
        self._use_field_names_in_headers = use_field_names_in_headers

    @property
    def df(self):
        if self._dataframe is None and self._raw and "headers" in self._raw:
            self._dataframe = self._build_df(
                self._raw, use_field_names_in_headers=self._use_field_names_in_headers
            )
        return self._dataframe


class EstimatesResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        content_data = data.get("content_data")
        inst = self.response_class(is_success=True, **data)
        inst.data = self.data_class(content_data, **kwargs)
        inst.data._owner = inst
        return inst


class EstimatesRequestFactory(RequestFactory):
    def get_query_parameters(self, *_, **kwargs) -> list:
        query_parameters = []
        universe = universe_arg_parser.get_str(kwargs.get("universe"), delim=",")
        query_parameters.append(("universe", universe))

        package = kwargs.get("package")
        if package is not None:
            package = package_estimates_arg_parser.get_str(package)
            query_parameters.append(("package", package))

        return query_parameters

    def extend_query_parameters(self, query_parameters, extended_params):
        # query_parameters -> [("param1", "val1"), ]
        result = dict(query_parameters)
        # result -> {"param1": "val1"}
        result.update(extended_params)
        # result -> {"param1": "val1", "extended_param": "value"}
        # return [("param1", "val1"), ("extended_param", "value")]
        return list(result.items())


package_estimates_arg_parser = make_enum_arg_parser(Package)

estimates_data_provider = DataProvider(
    request=EstimatesRequestFactory(),
    response=EstimatesResponseFactory(data_class=EstimatesData),
    validator=ESGAndEstimatesContentValidator(),
    parser=ESGAndEstimateParser(),
)
