# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Error Definitions for the package."""

from azureml._common._error_definition.user_error import (
    BadData, InvalidData
)
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings


# region BadData
class LabelingDataConversionFailed(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_CONVERSION_FAILED
# endregion


# region InvalidData
class LabelingDataDownloadFailed(InvalidData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_DOWNLOAD_FAILED
# endregion
