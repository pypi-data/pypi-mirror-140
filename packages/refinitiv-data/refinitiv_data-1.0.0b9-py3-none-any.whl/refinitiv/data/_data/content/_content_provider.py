from ..delivery.data import _data_provider


def get_invalid_universes(universes):
    result = []
    for universe in universes:
        if universe.get("Organization PermID") == "Failed to resolve identifier(s).":
            result.append(universe.get("Instrument"))
    return result


def get_universe_from_raw_response(raw_response):
    universe = raw_response.url.params["universe"]
    universe = universe.split(",")
    return universe


# ---------------------------------------------------------------------------
#   Raw data parser
# ---------------------------------------------------------------------------


class ESGAndEstimateParser(_data_provider.Parser):
    def process_failed_response(self, raw_response):
        parsed_data = super().process_failed_response(raw_response)
        status = parsed_data.get("status", {})
        error = status.get("error", {})
        errors = error.get("errors", [{}])
        reason = errors[0].get("reason")
        if reason:
            parsed_data["error_message"] += f": {reason}"

        return parsed_data


# ---------------------------------------------------------------------------
#   Content data validator
# ---------------------------------------------------------------------------


class ESGAndEstimatesContentValidator(_data_provider.ContentValidator):
    def validate_content_data(self, data):
        is_valid = super().validate_content_data(data)
        if not is_valid:
            return is_valid

        content_data = data.get("content_data", {})
        error = content_data.get("error", {})
        universes = content_data.get("universe")
        invalid_universes = get_invalid_universes(universes) if universes else []

        if error:
            is_valid = False
            data["error_code"] = error.get("code", -1)

            error_message = error.get("description")
            if error_message == "Unable to resolve all requested identifiers.":
                universe = get_universe_from_raw_response(data["raw_response"])
                error_message += f" Requested items: {universe}"

            if not error_message:
                error_message = error.get("message")
                errors = error.get("errors")
                if isinstance(errors, list):
                    error_message += ":\n"
                    error_message += "\n".join(map(str, errors))

            data["error_message"] = error_message

        elif invalid_universes:
            data["error_message"] = f"Failed to resolve identifiers {invalid_universes}"

        return is_valid


# ---------------------------------------------------------------------------
#   Provider layer
# ---------------------------------------------------------------------------


class ContentProviderLayer(_data_provider.DataProviderLayer):
    def __init__(self, content_type, **kwargs):
        _data_provider.DataProviderLayer.__init__(
            self,
            data_type=content_type,
            **kwargs,
        )
