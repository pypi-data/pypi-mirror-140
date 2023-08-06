import numpy
import pandas as pd

from ...legacy.tools import tz_replacer
from ...tools import to_datetime


def convert_content_data_to_df_rdp(content_data):
    columns = ["versionCreated", "text", "storyId", "sourceCode"]

    if isinstance(content_data, list):
        data = []
        for i in content_data:
            data.extend(i["data"])
    else:
        data = content_data["data"]
    first_created = [
        tz_replacer(headline["newsItem"]["itemMeta"]["firstCreated"]["$"])
        for headline in data
    ]
    first_created = numpy.array(first_created, dtype="datetime64")
    headlines = []

    for headline_data in data:
        news_item = headline_data.get("newsItem", dict())
        item_meta = news_item.get("itemMeta", {})
        info_sources = news_item["contentMeta"]["infoSource"]
        info_source = next(
            (
                item["_qcode"]
                for item in info_sources
                if item["_role"] == "sRole:source"
            ),
            None,
        )
        version_created = to_datetime(item_meta["versionCreated"]["$"])
        headlines.append(
            [
                version_created,
                item_meta["title"][0]["$"],
                headline_data["storyId"],
                info_source,
            ]
        )
    if headlines:
        dataframe = pd.DataFrame(
            data=headlines,
            index=first_created,
            columns=columns,
        )

        if not dataframe.empty:
            dataframe = dataframe.convert_dtypes()
        dataframe["versionCreated"] = dataframe["versionCreated"].tz_localize(None)

    else:
        dataframe = pd.DataFrame([], columns=columns)
    return dataframe


def _get_text_from_story(story):
    news_item = story.get("newsItem", dict())
    content_set = news_item.get("contentSet", dict())
    inline_data = content_set.get("inlineData", [dict()])
    return inline_data[0].get("$")


def _get_headline_from_story(story):
    news_item = story.get("newsItem", dict())
    content_meta = news_item.get("contentMeta", dict())
    headline = content_meta.get("headline", [dict()])
    return headline[0].get("$")


def get_headlines_rdp(raw, create_headline_func, limit):
    headlines = []
    if isinstance(raw, list):
        _data = []
        for i in raw:
            _data.extend(i.get("data", i.get("headlines", [])))
    else:
        _data = raw.get("data", raw.get("headlines", []))
    for datum in _data:
        headline = create_headline_func(datum)
        headlines.append(headline)
    headlines = headlines[:limit]
    return headlines
