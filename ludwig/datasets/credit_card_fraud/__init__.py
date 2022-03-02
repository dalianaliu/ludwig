#! /usr/bin/env python
# Copyright (c) 2019 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os

import pandas as pd

from sklearn.model_selection import train_test_split

from ludwig.datasets.base_dataset import BaseDataset, DEFAULT_CACHE_LOCATION
from ludwig.datasets.mixins.kaggle import KaggleDownloadMixin
from ludwig.datasets.mixins.load import CSVLoadMixin
from ludwig.datasets.registry import register_dataset
from ludwig.utils.fs_utils import makedirs, rename


def load(cache_dir=DEFAULT_CACHE_LOCATION, split=False, kaggle_username=None, kaggle_key=None):
    dataset = CreditCardFraud(cache_dir=cache_dir, kaggle_username=kaggle_username, kaggle_key=kaggle_key)
    return dataset.load(split=split)


@register_dataset(name="Credit_Card_Fraud")
class CreditCardFraud(CSVLoadMixin, KaggleDownloadMixin, BaseDataset):
    """The Credit Card Fraud dataset.

    This pulls in an array of mixins for different types of functionality which belongs in the workflow for ingesting
    and transforming training data into a destination dataframe that can be loaded by Ludwig's training API.
    """

    def __init__(self, cache_dir=DEFAULT_CACHE_LOCATION, kaggle_username=None, kaggle_key=None):
        self.kaggle_username = kaggle_username
        self.kaggle_key = kaggle_key
        self.is_kaggle_competition = False
        super().__init__(dataset_name="credit_card_fraud", cache_dir=cache_dir)

    def process_downloaded_dataset(self):
        """The final method where we create a concatenated CSV file with both training ant dest data."""
        train_file = self.config["csv_filename"]

        df = pd.read_csv(os.path.join(self.raw_dataset_path, train_file))
        train_df, test_df = train_test_split(df, test_size=0.1)

        train_df["split"] = 0
        test_df["split"] = 2

        df = pd.concat([train_df, test_df])

        makedirs(self.processed_temp_path, exist_ok=True)
        df.to_csv(os.path.join(self.processed_temp_path, self.csv_filename), index=False)
        rename(self.processed_temp_path, self.processed_dataset_path)