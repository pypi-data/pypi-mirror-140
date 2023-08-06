from typing import Callable

import pandas as pd

from ._content_type import ContentType
from ._df_build_type import DFBuildType
from .fundamental._df_builder import dfbuilder_udf, dfbuilder_rdp

content_type_by_build_type = {
    ContentType.DATA_GRID_RDP: {
        DFBuildType.INDEX: dfbuilder_rdp.build_index,
        DFBuildType.DATE_AS_INDEX: dfbuilder_rdp.build_date_as_index,
    },
    ContentType.DATA_GRID_UDF: {
        DFBuildType.INDEX: dfbuilder_udf.build_index,
        DFBuildType.DATE_AS_INDEX: dfbuilder_udf.build_date_as_index,
    },
}


def get_dfbuilder(
    dfbuild_type: DFBuildType, content_type: ContentType
) -> Callable[[any], pd.DataFrame]:
    builder_by_build_type = content_type_by_build_type.get(content_type)

    if not builder_by_build_type:
        raise ValueError(f"Cannot find mapping for content_type={content_type}")

    builder = builder_by_build_type.get(dfbuild_type)

    if not builder:
        raise ValueError(f"Cannot find mapping for dfbuild_type={dfbuild_type}")

    return builder
