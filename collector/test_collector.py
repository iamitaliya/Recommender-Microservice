import pytest
import collector
import pandas as pd


def test_data_download():
    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data = collector.data_download(url)
    assert data is not None, 'Test Passed: Files are downloaded'


def is_cleaned(test_data):
    data = collector.remove_na(test_data)
    assert data.isnotnull().values.any(), 'Test Passed: NA values are removed'


def has_duplicates(test_data):
    data = collector.remove_duplicates(test_data)
    assert not data.duplicate().any(), 'Test Passed: Duplicate values removed'


if __name__ == '__main__':
    pytest.main()
