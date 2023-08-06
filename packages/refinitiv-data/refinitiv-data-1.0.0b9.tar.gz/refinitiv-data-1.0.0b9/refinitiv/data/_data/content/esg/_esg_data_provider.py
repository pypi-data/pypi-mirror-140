from .._content_provider import ESGAndEstimatesContentValidator, ESGAndEstimateParser
from ...delivery.data._data_provider import (
    DataProvider,
    ResponseFactory,
    RequestFactory,
)
from ...tools import convert_content_data_to_df

# ---------------------------------------------------------------------------
#   Request
# ---------------------------------------------------------------------------
from ...tools import universe_arg_parser


class ESGRequestFactory(RequestFactory):
    def get_query_parameters(self, *args, **kwargs):
        query_parameters = []

        #
        # universe
        #
        universe = kwargs.get("universe")
        if universe:
            universe = universe_arg_parser.get_str(universe, delim=",")
            query_parameters.append(("universe", universe))

        #
        # start
        #
        start = kwargs.get("start")
        if start is not None:
            query_parameters.append(("start", start))

        #
        # end
        #
        end = kwargs.get("end")
        if end is not None:
            query_parameters.append(("end", end))

        return query_parameters


# ---------------------------------------------------------------------------
#   Response
# ---------------------------------------------------------------------------


class ESGResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        dataframe = convert_content_data_to_df(content_data)
        inst.data = self.data_class(content_data, dataframe)
        inst.data._owner = inst
        return inst


# ---------------------------------------------------------------------------
#   Provider
# ---------------------------------------------------------------------------

esg_data_provider = DataProvider(
    request=ESGRequestFactory(),
    response=ESGResponseFactory(),
    validator=ESGAndEstimatesContentValidator(),
    parser=ESGAndEstimateParser(),
)
