from typing import Iterable, Union, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ....tools import validate_types
from .._enums import Package

if TYPE_CHECKING:
    from ....content._types import OptBool, ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieves the estimates monthly historical snapshot value for recommendations for the last 12 months.

    Parameters
    ----------
    universe: str, list of str
        The Universe parameter allows the user to define the companies for which the content is returned.
        Ownership content is delivered at the Company Level. The user can use the following identifier types,
        there is no need to define what identifier type is being used:
            - Organization PermID
            - Instrument PermID
            - QuotePermID
            - RIC Code
            - ISIN
            - CUSIP
            - SEDOL
            - Valoren
            - Wert

    package: str, Package
        Packages of the content that are subsets in terms of breadth (number of fields)
        and depth (amount of history) of the overall content set. Wealth packages are defined as basic -
        A limited set of fields with a single historical point which could typically be considered 'Free to Air'
        content, standard - The common fields for a content set with a limited amount of history and professional -
        All fields and all history for a particular content set.
        Available values:
            - basic
            - standard
            - professional

    extended_params: ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import estimates
    >>> definition = estimates.view_summary.historical_snapshots_recommendations.Definition(universe="IBM.N", package=estimates.Package.BASIC, use_field_names_in_headers=True)
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        package: Union[str, Package],
        use_field_names_in_headers: "OptBool" = False,
        extended_params: "ExtendedParams" = None,
    ):
        validate_types(package, [str, Package], "package")

        super().__init__(
            content_type=ContentType.ESTIMATES_VIEW_SUMMARY_HISTORICAL_SNAPSHOTS_RECOMMENDATIONS,
            universe=universe,
            package=package,
            use_field_names_in_headers=use_field_names_in_headers,
            extended_params=extended_params,
        )
