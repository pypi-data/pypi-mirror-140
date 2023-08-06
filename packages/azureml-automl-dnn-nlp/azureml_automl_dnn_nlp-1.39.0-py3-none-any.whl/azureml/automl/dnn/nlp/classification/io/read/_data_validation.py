# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functions for data validation checks for the classification tasks."""

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TextDnnBadData
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.classification.common.constants import DatasetValidationConstants


def check_min_label_classes(train_df: pd.DataFrame, label_column_name: str):
    """Check if the training data contains a minimum number of unique class labels

    :param train_df: training dataframe
    :param label_column_name: Name/title of the label column
    :param is_multiclass: Bool flag to help distinguish between multiclass and multilabel
    """
    num_unique_label_classes = len(pd.unique(train_df[label_column_name]))

    if num_unique_label_classes < DatasetValidationConstants.MIN_LABEL_CLASSES:
        raise DataException._with_error(
            AzureMLError.create(TextDnnBadData,
                                error_details="Training data must contain at least two unique label classes",
                                target="num_unique_label_classes"))
