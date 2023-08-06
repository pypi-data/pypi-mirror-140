# coding: utf-8

__all__ = ["Definition"]

from typing import TYPE_CHECKING

from .._content_provider import ContentProviderLayer
from ...tools import create_repr

if TYPE_CHECKING:
    from .search_view_type import SearchViews


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve data for search metadata.

    Parameters
    ----------

    view : SearchViews
        picks a subset of the data universe to search against. see SearchViews

    Examples
    --------
    >>> from refinitiv.data.content import search
    >>> definition = search.metadata.Definition(view=search.SearchViews.PEOPLE)
    """

    def __init__(self, view: "SearchViews"):
        self._view = view

        from .. import ContentType

        super().__init__(
            content_type=ContentType.DISCOVERY_METADATA,
            view=self._view,
        )

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.search.metadata",
            content=f"{{view='{self._view}'}}",
        )
