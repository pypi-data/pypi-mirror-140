# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for reading input data."""

import logging
import os
import pandas as pd

import azureml.dataprep as dprep
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import LabelingDataDownloadFailed
from azureml.automl.core.shared.exceptions import DataException

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.dnn.nlp.common.constants import DataLabelingLiterals, Split
from azureml.core import Dataset as AmlDataset
from azureml.data.abstract_dataset import AbstractDataset
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def get_dataset_by_id(
        dataset_id: str,
        data_split: Split,
        workspace: Workspace
) -> AbstractDataset:
    """
    get dataset based on dataset id

    :param dataset_id: dataset id to retrieve
    :param data_split: Label for data split
    :param workspace: workspace to retrieve dataset from
    :return: dataset
    """
    Contract.assert_non_empty(
        dataset_id,
        "dataset_id",
        reference_code=ReferenceCodes._DNN_NLP_EMPTY_DATASET_ID,
        log_safe=True
    )
    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.DATA_FETCH}_{data_split.value}"
    ):
        ds = AmlDataset.get_by_id(workspace, dataset_id)
        _logger.info("Fetched {} data. Type: {}".format(data_split.value, type(ds)))
    return ds


def get_dataframe_from_dataset_id(
        workspace: Workspace,
        dataset_id: str,
        data_split: Split
) -> pd.DataFrame:
    """
    Get the train and val dataframes using the train and val dataset ids and the user's workspace

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param data_split: Label for data split
    :return: dataframe
    """
    ds = get_dataset_by_id(dataset_id, data_split, workspace)
    df = ds.to_pandas_dataframe()
    return df


def is_labeled_dataset(ds: AmlDataset) -> bool:
    """Check if the dataset is a labeled dataset. In the current approach, we rely on the presence of
    certain properties to check for labeled dataset.

    :param ds: Aml Dataset object
    :type ds: TabularDataset or TabularDataset (Labeled)
    :return: Labeled dataset or not
    :rtype: bool
    """
    return DataLabelingLiterals.IMAGE_COLUMN_PROPERTY in ds._properties


def download_file_dataset(
        dataset_id: str,
        data_split: Split,
        workspace: Workspace,
        ner_dir: str,
        overwrite: bool = True
) -> str:
    """
    load given dataset to data path and return the name of the file in reference

    :param dataset_id: dataset id to retrieve
    :param data_split: Label for data split
    :param workspace: workspace to retrieve dataset from
    :param ner_dir: directory where data should be downloaded
    :param overwrite: whether existing file can be overwritten
    :return: file name related to the dataset
    """
    _logger.info(f"Downloading file dataset for: {data_split.value} dataset")
    dataset = get_dataset_by_id(dataset_id, data_split, workspace)

    # to_path() returns format ["/filename.txt"], need to strip the "/"
    file_name = dataset.to_path()[0][1:]

    # Download data to ner_dir
    if not os.path.exists(ner_dir):
        os.makedirs(ner_dir)
    dataset.download(target_path=ner_dir, overwrite=overwrite)

    return file_name


def download_text_files_from_path_column(
        ds: AmlDataset,
        data_dir: str,
        data_label: Split,
        file_path_column: str = DataLabelingLiterals.IMAGE_URL
) -> None:
    """Download text files for NLP tasks

    :param ds: AML Dataset object
    :param data_dir: directory where data should be downloaded
    :param data_label: Label for data split
    :param file_path_column: Column that contains file path to download
    """
    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.LABELING_DATA_DOWNLOAD}_{data_label.value}"
    ):
        try:
            if is_labeled_dataset(ds):
                ds._dataflow.write_streams(file_path_column, dprep.LocalFileOutput(data_dir)).run_local()
            else:  # TabularDataset
                ds.download(file_path_column, data_dir, overwrite=True)
        except Exception as e:
            raise DataException._with_error(
                AzureMLError.create(
                    LabelingDataDownloadFailed, error_details=str(e), target=f"download_{data_label.value}_dataset")
            )
