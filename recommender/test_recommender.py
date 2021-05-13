import recommender
import pytest

movie = "The%20Godfather"


def is_cleaned():
    movie = recommender.clean_request(movie)
    assert "%20" not in movie, 'Test Passed: The request is cleaned'


if __name__ == '__main__':
    pytest.main()
