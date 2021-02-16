import pytest
import collector
import pandas as pd


def test_data_download():
    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data = collector.data_download(url)
    assert data is not None


def is_cleaned(test_data):
    data = collector.data_cleaning(test_data)
    assert data.isnull().values.any()
