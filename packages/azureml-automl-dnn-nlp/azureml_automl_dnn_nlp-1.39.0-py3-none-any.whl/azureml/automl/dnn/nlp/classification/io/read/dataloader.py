# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for the classification tasks."""

import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import Dataset as PyTorchDataset
from transformers import AutoTokenizer
from typing import Optional, Tuple

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import (
    PyTorchDatasetWrapper,
    PyTorchMulticlassDatasetWrapper
)
from azureml.automl.dnn.nlp.classification.io.read._data_validation import check_min_label_classes
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import load_datasets_for_labeling_service
from azureml.automl.dnn.nlp.classification.io.read.read_utils import get_y_transformer
from azureml.automl.dnn.nlp.classification.multiclass.utils import get_max_seq_length
from azureml.automl.dnn.nlp.classification.multilabel.utils import change_label_col_format
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split
from azureml.automl.dnn.nlp.common._data_utils import get_dataframe_from_dataset_id
from azureml.automl.dnn.nlp.validation.multilabel_validator import NLPMultilabelDataValidator
from azureml.core.workspace import Workspace


_logger = logging.getLogger(__name__)


def load_multiclass_dataset(
        dataset_id: str,
        validation_dataset_id: Optional[str],
        label_column_name: str,
        workspace: Workspace,
        tokenizer: AutoTokenizer,
        is_labeling_run: bool = False,
        download_dir: str = DataLiterals.DATA_DIR
) -> Tuple[PyTorchDataset,
           PyTorchDataset,
           np.ndarray,
           np.ndarray,
           Optional[np.ndarray],
           int]:
    """To get the training_set, validation_set and various label lists to generate metrics

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param label_column_name: Name/title of the label column
    :param workspace: workspace where dataset is stored in blob
    :param tokenizer: tokenizer to be used to tokenize the data
    :param is_labeling_run: Whether the experiment is from labeling service
    :param download_dir: Location to download file dataset into
    :return: training dataset, validation dataset, all class labels, train labels, y-validation, max sequence length
    """
    with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.DATA_PREPARATION
    ):
        if is_labeling_run:
            train_df, validation_df = load_datasets_for_labeling_service(
                workspace,
                dataset_id,
                validation_dataset_id,
                download_dir,
                include_label=True
            )
        else:
            train_df, validation_df = _dataset_loader(workspace, dataset_id, validation_dataset_id)
        check_min_label_classes(train_df, label_column_name)

        max_seq_length = get_max_seq_length(train_df, tokenizer, label_column_name)
        # Let's sort it for determinism
        train_label_list = np.sort(pd.unique(train_df[label_column_name]))
        label_list = train_label_list
        validation_set = None
        y_val = None
        if validation_df is not None:
            y_val = validation_df[label_column_name].values
            validation_df.drop(columns=label_column_name, inplace=True)
            val_label_list = pd.unique(y_val)
            label_list = np.union1d(train_label_list, val_label_list)
            validation_set = PyTorchMulticlassDatasetWrapper(validation_df, train_label_list, tokenizer,
                                                             max_seq_length, label_column_name=None)
        training_set = PyTorchMulticlassDatasetWrapper(train_df, train_label_list, tokenizer,
                                                       max_seq_length, label_column_name=label_column_name)

    return training_set, validation_set, label_list, train_label_list, y_val, max_seq_length


def load_and_validate_multilabel_dataset(
        dataset_id: str,
        validation_dataset_id: Optional[str],
        label_column_name: str,
        workspace: Workspace,
        dataset_language: Optional[str] = 'eng',
        is_labeling_run: bool = False,
        download_dir: str = DataLiterals.DATA_DIR
) -> Tuple[PyTorchDataset, PyTorchDataset, int, MultiLabelBinarizer]:
    """To get the training_set, validation_set and num_label_columns for multilabel scenario

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param label_column_name: Name/title of the label column
    :param workspace: Workspace where dataset is stored in blob
    :param dataset_language: language code of dataset
    :param is_labeling_run: Whether the experiment is from labeling service
    :param download_dir: Location to download file dataset into
    :return: training dataset, validation dataset, num of label columns, y_transformer
    """
    if is_labeling_run:
        train_df, validation_df = load_datasets_for_labeling_service(
            workspace,
            dataset_id,
            validation_dataset_id,
            download_dir,
            include_label=True
        )
    else:
        train_df, validation_df = _dataset_loader(workspace, dataset_id, validation_dataset_id)

    warning_message = "You are using the old format of label column. "
    warning_message += "It may parse wrong labels. "
    warning_message += "Please update your label column format to the new format"
    # TODO: add the link of new format into warning message
    if train_df.loc[0, label_column_name][0] != "[":
        _logger.warning(warning_message)
        change_label_col_format(train_df, label_column_name)
    if validation_df is not None:
        if validation_df.loc[0, label_column_name][0] != "[":
            _logger.warning(warning_message)
            change_label_col_format(validation_df, label_column_name)

    # data validation
    validator = NLPMultilabelDataValidator()
    validator.validate(label_column_name, train_df, validation_df)

    # Fit a MultiLabelBinarizer on the label column so that we can transform labels column
    y_transformer = get_y_transformer(train_df, validation_df, label_column_name)
    num_label_cols = len(y_transformer.classes_)

    # Convert dataset into the format ingestible be model
    _logger.info("TRAIN Dataset: {}".format(train_df.shape))
    training_set = PyTorchDatasetWrapper(train_df, dataset_language, label_column_name=label_column_name,
                                         y_transformer=y_transformer)
    validation_set = None
    if validation_df is not None:
        _logger.info("VALIDATION Dataset: {}".format(validation_df.shape))
        validation_set = PyTorchDatasetWrapper(validation_df, dataset_language,
                                               label_column_name=label_column_name,
                                               y_transformer=y_transformer)
    return training_set, validation_set, num_label_cols, y_transformer


def _dataset_loader(
        workspace: Workspace,
        dataset_id: str,
        validation_dataset_id: Optional[str]
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Get the train and val dataframes using the train and val dataset ids and the user's workspace

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param workspace: workspace where dataset is stored in blob
    :return: training dataframe, validation dataframe
    """
    train_df = get_dataframe_from_dataset_id(
        workspace, dataset_id, Split.train
    )
    validation_df = None
    if validation_dataset_id:
        validation_df = get_dataframe_from_dataset_id(
            workspace, validation_dataset_id, Split.valid
        )
    return train_df, validation_df
