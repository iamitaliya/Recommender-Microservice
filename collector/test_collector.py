import pytest
import collector
import pandas as pd
import requests

test_data = pd.DataFrame({
    'A': ['spam', None, 'spam', 'eggs'] * 6,
    'B': ['alpha', 'beta', 'gamma'] * 8, })


def test_data_download():
    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data = collector.data_download(url)
    assert data is not None, 'Test Passed: Files are downloaded'

def test_movielens_connection():
    res = requests.get("http://files.grouplens.org/datasets/movielens/ml-latest-small.zip").status_code
    return res == 200

def test_is_cleaned():
    data = collector.remove_na(test_data)
    return not data.isnull().values.any()
    # assert not data.isnull().values.any(), 'Test Passed: NA values are removed'


def test_has_duplicates():
    data = collector.remove_duplicates(test_data)
    return not data.duplicated().any()
    # assert not data.duplicated().any(), 'Test Passed: Duplicate values removed'

# # Test if db connection is successfully established or not
def test_db_connection():
    try:
        conn = collector.database_connection()
        return conn.closed == 0
    except:
        return False

def unit_test():
    tests = {}
    tests["Data Cleaning Test:"] = test_is_cleaned()
    tests["Data Duplicate Test:"] = test_has_duplicates()
    tests["MovieLens Connection:"] = test_movielens_connection()
    tests["Database Connection:"] = test_db_connection()
    print("Found", len(tests), "tests..." )
    for test, result in tests.items():
        print(test, "PASSED" if result else "FAILED")
    print(sum(tests.values()), "out of", len(tests.values()), "tests passed." )
    return all(tests.values())


if __name__ == '__main__':
    pytest.main()
