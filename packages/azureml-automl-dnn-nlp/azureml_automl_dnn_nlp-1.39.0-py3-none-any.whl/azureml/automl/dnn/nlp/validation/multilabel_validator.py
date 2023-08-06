# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This module is for data validation purpose for dnn nlp multilabel scenario
"""

from .validators import AbstractNLPClassificationDataValidator
from .utils import raise_validation_error
from typing import Optional, Set, Tuple

from azureml.automl.dnn.nlp.common.constants import ValidationLiterals

import ast
import numpy as np
import pandas as pd


class NLPMultilabelDataValidator(AbstractNLPClassificationDataValidator):
    """Data validation class for multilabel scenario only"""

    def check_custom_validation(
        self,
        label_col_name: str,
        train_data: pd.DataFrame,
        valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Data validation for multilabel scenario only.

        Validation includes:
            1. check if we can apply eval function on label column
            2. check if all elements are list for in label column
            3. check not all samples have exactly one label
            4. check if all elements in the lists are integers or strings
            5. check if the string versions of integer values are not already in the strings


        Do not check unique label values as it is in check_shared_validation

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate
        :return: None
        """
        labels = self._check_eval_label_column(
            train_data,
            label_col_name,
            ValidationLiterals.TRAINING_SET
        )
        if valid_data is not None:
            valid_labels = self._check_eval_label_column(
                train_data,
                label_col_name,
                ValidationLiterals.VALID_SET
            )
            labels = np.concatenate([labels, valid_labels])

        error_message = "Validation Error: after eval, not all label values are lists"
        if not all(isinstance(x, list) for x in labels):
            raise_validation_error(error_message)

        error_message = "Validation Error: all samples have exactly one label. Use Multiclass classification instead."
        if all(len(label) == 1 for label in labels):
            raise_validation_error(error_message)

        int_set, str_set = self._check_label_types(labels)

        error_message = "Validation Error: Found same label in both str and int format"
        int_set = set([str(label) for label in int_set])
        if not len(int_set & str_set) == 0:
            raise_validation_error(error_message)

    def _check_eval_label_column(self, data: pd.DataFrame, label_col_name: str, data_source: str) -> np.ndarray:
        """
        try to apply eval function on the label column and return result if possible

        :param data: training set data or validation set data
        :param label_col_name: column name of label column
        :param data_source: "train", "validation" or "test" for more informative error message
        :return the numpy array of label column after passing ast.literal_eval
        """
        try:
            labels = data[label_col_name].apply(ast.literal_eval)
        except:
            error_message = "Validation Error: Failed to apply `ast.literal_eval`"
            error_message += f" on label column for {data_source} dataset."
            raise_validation_error(error_message)
        return labels.values

    def _check_label_types(self, labels: np.ndarray) -> Tuple[Set[int], Set[str]]:
        int_set = set()  # type: Set[int]
        str_set = set()  # type: Set[str]
        error_message = "Validation Error: Expecting all labels to have type int or str, but found {}"
        # TODO: think about optimization of this
        for label_set in labels:
            int_labels = []
            str_labels = []
            for label in label_set:
                if isinstance(label, int):
                    int_labels.append(label)
                elif isinstance(label, str):
                    str_labels.append(label)
                else:
                    raise_validation_error(error_message.format(type(label)))
            int_set |= set(int_labels)
            str_set |= set(str_labels)
        return int_set, str_set
