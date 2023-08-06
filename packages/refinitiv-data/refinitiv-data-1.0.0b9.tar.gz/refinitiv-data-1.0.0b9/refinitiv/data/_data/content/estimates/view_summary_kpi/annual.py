from typing import Iterable, Union, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType

if TYPE_CHECKING:
    from ....content._types import OptBool, ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieves estimates summary values for KPI measures for annual periods.

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

    extended_params: ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import estimates
    >>> definition = estimates.view_summary_kpi.annual.Definition(universe="ORCL.N", use_field_names_in_headers=True)
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        use_field_names_in_headers: "OptBool" = False,
        extended_params: "ExtendedParams" = None,
    ):
        super().__init__(
            content_type=ContentType.ESTIMATES_VIEW_SUMMARY_KPI_ANNUAL,
            universe=universe,
            use_field_names_in_headers=use_field_names_in_headers,
            extended_params=extended_params,
        )
