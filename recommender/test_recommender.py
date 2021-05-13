import pytest
import recommender


def test_is_cleaned():
    movie = "The%20Godfather"
    movie = recommender.clean_request(movie)
    assert "%20" not in movie, 'Test Passed: The request is cleaned'


if __name__ == '__main__':
    pytest.main()
