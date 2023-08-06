from ...core.session import SessionType, get_valid_session
from ...delivery.data._data_provider import DataProviderLayer

NEWS_UNDERLYING_PLATFORM_KEY = "apis.data.news.underlying-platform"


class NewsDataProviderLayer(DataProviderLayer):
    async def get_data_async(self, session=None, on_response=None, *args, **kwargs):
        from .. import ContentType

        udf_news_content_type_by_rdp = {
            ContentType.NEWS_STORY_RDP: ContentType.NEWS_STORY_UDF,
            ContentType.NEWS_HEADLINES_RDP: ContentType.NEWS_HEADLINES_UDF,
        }

        session = get_valid_session(session)
        underlying_platform = session.config.get(NEWS_UNDERLYING_PLATFORM_KEY) or "rdp"
        if underlying_platform not in {"rdp", "udf"}:
            message = (
                f"Not correct value for '{NEWS_UNDERLYING_PLATFORM_KEY}'. "
                "Possible values: 'udf', 'rdp'"
            )
            session.error(message)
            raise ValueError(message)
        if underlying_platform == "udf":
            if session.type == SessionType.PLATFORM:
                session.debug(
                    "UDF News service cannot be used with platform sessions, RDP News will be used instead. "
                    f"The '{NEWS_UNDERLYING_PLATFORM_KEY}' = 'udf' parameter "
                    "will be discarded, meaning that the regular RDP News service "
                    "will be used for News Story and News Headlines data requests."
                )
            else:
                content_type = udf_news_content_type_by_rdp.get(self._data_type)
                self._initialize(content_type, **self._kwargs)

        response = await super().get_data_async(session, on_response, **kwargs)
        return response
