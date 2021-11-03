import pytest
import recommender


def test_is_cleaned():
    movie = "The%20Godfather"
    movie = recommender.clean_request(movie)
    return "%20" not in movie

def test_recommend():
    recomendation = ""
    try:
        recomendation = recommender.recommend(5)
    except:
        return False
    return not recomendation

def test_get_movie_id():
    movie_name = "Iron Man (2008)"
    try:
        movie_id = recommender.get_movie_id(movie_name)
    except:
        return False
    return movie_id != 0

# # Test if db connection is successfully established or not
def test_db_connection():
    try:
        conn = recommender.database_connection()
        return conn.closed == 0
    except:
        return False

def unit_test():
    tests = {}
    tests["Data Cleaning Test:"] = test_is_cleaned()
    # tests["Recommendation Test:"] = test_recommend()  # it may not work if there is not data in database i.e. running for the first time
    # tests["Get Movie ID Test:"] = test_get_movie_id()
    tests["Database Connection:"] = test_db_connection()
    print("Found", len(tests), "tests..." )
    for test, result in tests.items():
        print(test, "PASSED" if result else "FAILED")
    print(sum(tests.values()), "out of", len(tests.values()), "tests passed." )
    return all(tests.values())

if __name__ == '__main__':
    pytest.main()
