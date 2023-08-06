# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This module contains utility functions for data validation for dnn nlp
"""

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TextDnnBadData
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals


def raise_validation_error(error_message: str) -> None:
    """
    Raise DataException with given error_message

    :param error_message: the error message
    :return None
    """
    raise DataException._with_error(
        AzureMLError.create(
            TextDnnBadData,
            error_details=error_message,
            target=ValidationLiterals.DATA_EXCEPTION_TARGET
        )
    )
