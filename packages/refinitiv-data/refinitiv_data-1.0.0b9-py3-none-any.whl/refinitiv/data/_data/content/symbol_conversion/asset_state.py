from enum import Enum, unique

__all__ = ["AssetState"]


@unique
class AssetState(Enum):
    """
    Asset state values for 'filter' parameter in request for SymbolConversion content object.
    """

    ACTIVE = "Active"
    INACTIVE = "Inactive"
