from typing import Dict, Iterable, Union

import pandas as pd

from ...delivery.data._data_provider import (
    Data,
    DataProvider,
    RequestFactory,
    ResponseFactory,
    Parser,
)
from ...delivery.data.endpoint import RequestMethod

# --------------------------------------------------------------------------------------
#   Response
# --------------------------------------------------------------------------------------
from refinitiv.data._data.tools import get_error_reason_from_parsed_data


def _get_unique_keys(list_of_dict: Iterable[Dict]) -> list:
    keys = []
    unique_keys = set()

    for item in list_of_dict:
        unique_keys.update(item)
        if len(keys) < len(item):
            keys = list(item.keys())

    diff_set = unique_keys - set(keys)
    if diff_set:
        keys += diff_set

    return keys


def convert_search_json_to_pandas(json_data: dict) -> Union[None, pd.DataFrame]:
    if "Hits" not in json_data:
        return None

    hits = json_data["Hits"]
    keys = _get_unique_keys(hits)
    hit_dataframe = {key: [item.get(key) for item in hits] for key in keys}

    if hit_dataframe:
        _data_frame = pd.DataFrame(hit_dataframe)
        if not _data_frame.empty:
            _data_frame.fillna(pd.NA, inplace=True)
            _data_frame = _data_frame.convert_dtypes()
        return _data_frame

    return pd.DataFrame([])


class SearchResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        dataframe = convert_search_json_to_pandas(content_data)
        inst.data = self.data_class(content_data, dataframe)
        inst.total = content_data.get("Total")
        return inst


def _convert_lookup_json_to_df(json_data: dict) -> Union[None, pd.DataFrame]:
    if "Matches" not in json_data:
        return None

    match_df = {}
    matches = json_data["Matches"]
    matches_list_of_dict = list(matches.values())
    property_names = _get_unique_keys(matches_list_of_dict)

    for match_name, match_value_dict in matches.items():
        for property_name in property_names:
            match_property_df_dict = match_df.setdefault(property_name, {})

            get_name = match_value_dict.get(property_name)
            match_property_df_dict[match_name] = get_name

    if match_df:
        df = pd.DataFrame(match_df)
        if not df.empty:
            df.fillna(pd.NA, inplace=True)
            return df.convert_dtypes()
        return df

    return pd.DataFrame([])


class LookupResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        dataframe = _convert_lookup_json_to_df(content_data)
        inst.data = self.data_class(content_data, dataframe)
        return inst


#   response data keyword
_ResponsePropertiesName = "Properties"
_ResponseTypeName = "Type"

#       flags
_ResponseFlagNames = [
    _ResponseTypeName,
    # flags
    "Searchable",
    "Sortable",
    "Navigable",
    "Groupable",
    "Exact",
    "Symbol",
]


def _extend_tuple_with_last_element(input_tuple, num_expected_tuple_elements):
    """do extend the input tuple by duplicate last element value to be the
    expected number of tuple elements"""
    num_input_tuple_elements = len(input_tuple)
    return input_tuple + input_tuple[num_input_tuple_elements - 1 :] * (
        num_expected_tuple_elements - num_input_tuple_elements
    )


def _convert_property_attributes(
    property_attribute_to_property_dict_dict,
    property_name,
    ancestor_property_name_type,
    property_attribute_dict,
):
    """convert each property into a dictionary of property attribute
    to property dictionary"""
    #   depth of this property
    this_property_depth = 1

    #   determine this attribute name tuple
    attribute_name_type = ancestor_property_name_type[:] + (property_name,)

    #   check the attribute type is nested or not?
    property_attribute_type = property_attribute_dict[_ResponseTypeName]
    if property_attribute_type == "Nested":
        #   this property is a nested type, recursive convert this property attribute
        #   extract properties of this nested type
        this_properties_of_nested_type = property_attribute_dict[
            _ResponsePropertiesName
        ]

        #   loop over all nested attributes and convert it
        for (
            nested_property_name,
            nested_property_attribute_dict,
        ) in this_properties_of_nested_type.items():
            #   call convert recusivly for nested type
            _convert_property_attributes(
                property_attribute_to_property_dict_dict,
                nested_property_name,
                attribute_name_type,
                nested_property_attribute_dict,
            )

        #   increase property depth by one
        this_property_depth += 1

    #   convert the attribute flags of this property attributes
    #       loop over all possible attributes and convert it
    for property_attribute_name in _ResponseFlagNames:
        #   add properties of properties to dict of dict
        #       fill with None if the properties doesn't exist
        property_dict = property_attribute_to_property_dict_dict.setdefault(
            property_attribute_name, {}
        )
        property_dict[attribute_name_type] = property_attribute_dict.get(
            property_attribute_name, False
        )

    return this_property_depth


def convert_metadata_json_to_pandas(json_data: dict) -> Union[None, pd.DataFrame]:
    """parse the metadata response from dict of dict to be a dict of dict tuple"""
    if _ResponsePropertiesName not in json_data:
        return None

    property_attribute_to_property_dict_dict = {}
    property_name_to_depth_dict = {}

    properties = json_data[_ResponsePropertiesName]

    #   loop over view metadata and convert it to dict of dict tuple
    for property_name, property_attribute_dict in properties.items():
        #   do convert each property attributes into dict of dict
        this_property_depth = _convert_property_attributes(
            property_attribute_to_property_dict_dict,
            property_name,
            (),
            property_attribute_dict,
        )

        #   store each property depth as dict
        property_name_to_depth_dict[property_name] = this_property_depth

    ######################################################
    #   convert response to be a dataframe format
    # warning OPTIMIZE_ME :: THIS CAN BE OPTIMIZE

    #   determine the maximum depth on nested property
    max_property_depth = max(property_name_to_depth_dict.values())

    #   loop over all the propertyAttributeToPropertyDictDict and convert to a dataframe format
    dataframe = {}
    for (
        property_attribute_name,
        property_dict,
    ) in property_attribute_to_property_dict_dict.items():
        for property_key, property_value in property_dict.items():
            #   construct the property attribute for this property
            dataframe_property_dict = dataframe.setdefault(property_attribute_name, {})

            #   construct the key of dataframe property
            dataframe_property_key = _extend_tuple_with_last_element(
                property_key, max_property_depth
            )
            dataframe_property_dict[dataframe_property_key] = property_value

    if len(dataframe) == 0:
        return pd.DataFrame([])

    return pd.DataFrame(dataframe).convert_dtypes()


class MetadataResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        dataframe = convert_metadata_json_to_pandas(content_data)
        inst.data = self.data_class(content_data, dataframe)
        return inst


# --------------------------------------------------------------------------------------
#   Request
# --------------------------------------------------------------------------------------


class BaseSearchRequestFactory(RequestFactory):
    _mapping_parameter_names = {}

    def get_body_parameters(self, *_, **kwargs) -> dict:
        body_parameters = {
            self._mapping_parameter_names[key]: value
            for key, value in kwargs.items()
            if key in self._mapping_parameter_names and value
        }

        view = kwargs.get("view")
        if view:
            body_parameters["View"] = view.value

        return body_parameters

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return RequestMethod.POST


class SearchRequestFactory(BaseSearchRequestFactory):
    _mapping_parameter_names = {
        "boost": "Boost",
        "features": "Features",
        "filter": "Filter",
        "group_by": "GroupBy",
        "group_count": "GroupCount",
        "navigators": "Navigators",
        "order_by": "OrderBy",
        "query": "Query",
        "scope": "Scope",
        "select": "Select",
        "skip": "Skip",
        "terms": "Terms",
        "top": "Top",
    }


class LookupRequestFactory(BaseSearchRequestFactory):
    _mapping_parameter_names = {
        "boost": "Boost",
        "filter": "Filter",
        "scope": "Scope",
        "select": "Select",
        "terms": "Terms",
    }


class MetadataRequestFactory(RequestFactory):
    def get_query_parameters(self, *_, **kwargs):
        view = kwargs["view"]
        return view.value

    def add_query_parameters(self, url, query_parameters) -> str:
        return f"{url}/{query_parameters}"


# --------------------------------------------------------------------------------------
#   Parser
# --------------------------------------------------------------------------------------


class LookupParser(Parser):
    def process_failed_response(self, raw_response):
        parsed_data = super().process_failed_response(raw_response)
        reason = get_error_reason_from_parsed_data(parsed_data)
        if reason:
            parsed_data["error_message"] += f": {reason}"
        return parsed_data


search_data_provider = DataProvider(
    request=SearchRequestFactory(),
    response=SearchResponseFactory(data_class=Data),
)

lookup_data_provider = DataProvider(
    request=LookupRequestFactory(),
    response=LookupResponseFactory(data_class=Data),
    parser=LookupParser(),
)

metadata_data_provider = DataProvider(
    request=MetadataRequestFactory(),
    response=MetadataResponseFactory(data_class=Data),
)
