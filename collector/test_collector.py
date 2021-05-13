import pytest
import collector
import pandas as pd

test_data = dft = pd.DataFrame({
    'A': ['spam', None, 'spam', 'eggs'] * 6,
    'B': ['alpha', 'beta', 'gamma'] * 8, })


def test_data_download():
    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data = collector.data_download(url)
    assert data is not None, 'Test Passed: Files are downloaded'


def test_is_cleaned():
    data = collector.remove_na(test_data)
    assert not data.isnull().values.any(), 'Test Passed: NA values are removed'


def test_has_duplicates():
    data = collector.remove_duplicates(test_data)
    assert not data.duplicated().any(), 'Test Passed: Duplicate values removed'


if __name__ == '__main__':
    pytest.main()
