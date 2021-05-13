import recommender
import pytest


def is_cleaned(movie):
    movie = recommender.clean_request(movie)
    assert "%20" not in movie, 'Test Passed: The request is cleaned'


if __name__ == '__main__':
    pytest.main()
