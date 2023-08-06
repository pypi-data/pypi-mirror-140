import pandas as pd

from .data_classes import Headline, Story, StoryUDF, HeadlineUDF
from .sort_order import SortOrder
from .tools import (
    convert_content_data_to_df_rdp,
    get_headlines_rdp,
)
from .._join_responses import join_responses
from ...core.session import DesktopSession
from ...delivery.data._data_provider import (
    DataProvider,
    RequestFactory,
    ResponseFactory,
    Response,
    Data,
    ContentValidator,
)
from ...delivery.data.endpoint import RequestMethod
from ...legacy.tools import convert_content_data_to_df_udf
from ...tools import to_datetime, make_enum_arg_parser

MAX_LIMIT = 100


class NewsStoryData(Data):
    def __init__(self, raw, *args, **kwargs):
        super().__init__(raw)
        self._story = None

    @property
    def raw(self):
        return self._raw

    @property
    def story(self):
        if self._story is None:
            self._story = Story.create(self._raw)
        return self._story


class NewsStoryDataUDF(NewsStoryData):
    def __init__(self, raw, *args, **kwargs):
        super().__init__(raw)

    @property
    def story(self):
        if self._story is None:
            self._story = StoryUDF.create(self._raw)
        return self._story


class NewsHeadlinesDataRDP(Data):
    def __init__(self, raw, dataframe=None):
        super().__init__(raw, dataframe)
        if dataframe is None:
            dataframe = pd.DataFrame()
        self._dataframe = dataframe
        self._headlines = None
        self._limit = None

    @property
    def headlines(self):
        if self._headlines is None:
            self._headlines = []
            self._headlines = get_headlines_rdp(self.raw, Headline.create, self._limit)

        return self._headlines


class NewsHeadlinesDataUDF(Data):
    def __init__(self, raw, dataframe=None):
        super().__init__(raw, dataframe)
        self._headlines = None
        self._limit = None

    @property
    def headlines(self):
        if self._headlines is None:
            self._headlines = []
            self._headlines = get_headlines_rdp(
                self.raw, HeadlineUDF.create, self._limit
            )

        return self._headlines


class NewsStoryResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        _raw = None
        if self.is_success:
            _raw = self.data
        self._data = NewsStoryData(_raw)

    def __str__(self):
        if self._data and self._data.raw:
            return self._data.raw["newsItem"]["contentSet"]["inlineData"][0]["$"]
        else:
            return f"{self.errors}"

    @property
    def html(self):
        if self._data and self._data.raw:
            return (
                self._data.raw.get("newsItem", {})
                .get("contentSet", {})
                .get("inlineXML", [{}])[0]
                .get("$")
            )
        else:
            return None

    @property
    def text(self):
        if self._data and self._data.raw:
            return self._data.raw["newsItem"]["contentSet"]["inlineData"][0]["$"]
        else:
            return None


class NewsContentValidatorUDF(ContentValidator):
    def validate_content_data(self, data):
        is_valid = super().validate_content_data(data)
        content_data = data.get("content_data")
        if not is_valid:
            return is_valid

        if "ErrorCode" in content_data:
            data["error_code"] = content_data.get("ErrorCode")
            data["error_message"] = content_data.get("ErrorMessage")
            is_valid = False
        elif not content_data:
            is_valid = False
            data["error_code"] = 1
            data["error_message"] = "Content data not contain any data"

        return is_valid


class NewsHeadlinesResponseFactory(ResponseFactory):
    def create_success(self, data, *args, **kwargs):
        convert_function = kwargs.get(
            "convert_function", convert_content_data_to_df_rdp
        )
        content_data = data.get("content_data")
        inst = self.response_class(is_success=True, **data)
        dataframe = convert_function(content_data)
        inst.data = self.data_class(content_data, dataframe)
        inst.data._owner = inst
        return inst


class NewsHeadlinesRequestFactoryUDF(RequestFactory):
    def extend_body_parameters(self, body_parameters, extended_params):
        body_parameters["Entity"]["W"].update(extended_params)
        return body_parameters

    def get_body_parameters(self, *args, **kwargs):
        entity = {
            "E": "News_Headlines",
        }
        w = dict()

        query = kwargs.get("query")
        w["query"] = query

        count = kwargs.get("count")
        if count is not None:
            w["number"] = str(count)

        payload = kwargs.get("payload")
        if payload is not None:
            w["payload"] = payload

        repository = kwargs.get("repository")
        if repository is not None:
            w["repository"] = repository

        session = args[0]
        app_key = session.app_key
        w["productName"] = app_key

        date_from = kwargs.get("date_from")
        if date_from is not None:
            w["dateFrom"] = to_datetime(date_from).isoformat()

        date_to = kwargs.get("date_to")
        if date_to is not None:
            w["dateTo"] = to_datetime(date_to).isoformat()

        entity["W"] = w
        body_parameters = {"Entity": entity}
        return body_parameters

    def get_url(self, *args, **kwargs):
        session = args[0]
        url = session._get_rdp_url_root()
        if isinstance(session, DesktopSession):
            url = session._get_udf_url()
        return url

    def update_url(self, url_root, url, path_parameters, query_parameters):
        return url

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return RequestMethod.POST


class NewsStoryRequestFactoryUDF(RequestFactory):
    def get_body_parameters(self, *args, **kwargs):
        entity = {
            "E": "News_Story",
        }
        w = dict()

        story_id = kwargs.get("story_id")
        w["storyId"] = story_id

        session = args[0]
        app_key = session.app_key
        w["productName"] = app_key

        entity["W"] = w
        body_parameters = {"Entity": entity}
        return body_parameters

    def get_url(self, *args, **kwargs):
        session = args[0]
        url = session._get_rdp_url_root()
        if isinstance(session, DesktopSession):
            url = session._get_udf_url()
        return url

    def update_url(self, url_root, url, path_parameters, query_parameters):
        return url

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return RequestMethod.POST


class NewsHeadlinesRequestFactoryRDP(RequestFactory):
    def extend_query_parameters(self, query_parameters, extended_params):
        # query_parameters -> [("param1", "val1"), ]
        result = dict(query_parameters)
        # result -> {"param1": "val1"}
        result.update(extended_params)
        # result -> {"param1": "val1", "extended_param": "value"}
        # return [("param1", "val1"), ("extended_param", "value")]
        return list(result.items())

    def get_query_parameters(self, *_, **kwargs):
        query_parameters = []

        query = kwargs.get("query")
        query_parameters.append(("query", query))

        count = kwargs.get("count")
        if count is not None:
            query_parameters.append(("limit", count))

        date_from = kwargs.get("date_from")
        if date_from is not None:
            date_from = to_datetime(date_from).isoformat()
            query_parameters.append(("dateFrom", date_from))

        date_to = kwargs.get("date_to")
        if date_to is not None:
            date_to = to_datetime(date_to).isoformat()
            query_parameters.append(("dateTo", date_to))

        sort_order = kwargs.get("sort_order")
        if sort_order is not None:
            sort_order = sort_order_news_arg_parser.get_str(sort_order)
            query_parameters.append(("sort", sort_order))

        # for pagination
        cursor = kwargs.get("cursor")
        if cursor is not None:
            query_parameters.append(("cursor", cursor))

        return query_parameters


class NewsStoryRequestFactoryRDP(RequestFactory):
    def get_path_parameters(self, *_, **kwargs):
        story_id = kwargs.get("story_id")
        path_parameters = {"storyId": story_id}
        return path_parameters

    def get_header_parameters(self, *args, **kwargs):
        header_parameters = {"accept": "application/json"}
        return header_parameters

    def get_url(self, *args, **kwargs):
        return super().get_url(*args, **kwargs) + "/{storyId}"


class NewsHeadlinesDataProviderRDP(DataProvider):
    async def get_data_async(self, *args, **kwargs):
        on_page_response = kwargs.get("on_page_response")
        limit = kwargs.get("count")
        responses = []
        _kwargs = kwargs
        if limit > MAX_LIMIT:
            _kwargs["count"] = MAX_LIMIT
        for i in range(0, limit, MAX_LIMIT):
            response = await super().get_data_async(*args, **_kwargs)
            responses.append(response)
            if on_page_response:
                on_page_response(self, response)
            meta = response.data.raw.get("meta", {})
            _next = meta.get("next")
            _kwargs = {"cursor": _next}
        response = join_responses(responses, data_class=NewsHeadlinesDataRDP)
        response.data._limit = limit
        response.data._dataframe = response.data._dataframe[:limit]
        return response


class NewsStoryResponseFactory(ResponseFactory):
    @staticmethod
    def change_code_and_message_in_data(data: dict) -> dict:
        new_error_msg = "Error while calling the NEP backend: Story not found"
        error_code = data.get("error_code") or 0
        error_msg = data.get("error_message") or ""

        if error_code == 400 or error_code == 404 and new_error_msg != error_msg:
            data["error_code"] = 404
            data["error_message"] = new_error_msg

        return data

    def create_fail(self, *args, **kwargs):
        data = args[0]
        self.change_code_and_message_in_data(data)
        return super().create_fail(*args, **kwargs)


class NewsDataProviderUDF(DataProvider):
    async def get_data_async(self, *args, **kwargs):
        limit = kwargs.get("count")
        responses = []
        _kwargs = kwargs
        if limit and limit > MAX_LIMIT:
            _kwargs["count"] = MAX_LIMIT

            for _ in range(0, limit, MAX_LIMIT):
                response = await super().get_data_async(
                    convert_function=convert_content_data_to_df_udf, *args, **_kwargs
                )
                responses.append(response)
            response = join_responses(responses, data_class=self.response.data_class)
            response.data._limit = limit
            response.data._dataframe = response.data._dataframe[:limit]
        else:
            response = await super().get_data_async(
                convert_function=convert_content_data_to_df_udf, *args, **_kwargs
            )
        return response


sort_order_news_arg_parser = make_enum_arg_parser(SortOrder)

news_headlines_data_provider_rdp = NewsHeadlinesDataProviderRDP(
    response=NewsHeadlinesResponseFactory(data_class=NewsHeadlinesDataRDP),
    request=NewsHeadlinesRequestFactoryRDP(),
)
news_headlines_data_provider_udf = NewsDataProviderUDF(
    response=NewsHeadlinesResponseFactory(data_class=NewsHeadlinesDataUDF),
    request=NewsHeadlinesRequestFactoryUDF(),
    validator=NewsContentValidatorUDF(),
)

news_story_data_provider_rdp = DataProvider(
    response=NewsStoryResponseFactory(
        response_class=NewsStoryResponse, data_class=NewsStoryData
    ),
    request=NewsStoryRequestFactoryRDP(),
)

news_story_data_provider_udf = NewsDataProviderUDF(
    response=NewsStoryResponseFactory(
        response_class=NewsStoryResponse, data_class=NewsStoryDataUDF
    ),
    request=NewsStoryRequestFactoryUDF(),
    validator=NewsContentValidatorUDF(),
)
