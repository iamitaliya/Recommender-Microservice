from flask import Flask, json, jsonify, request
from flask_cors import CORS, cross_origin
import psycopg2
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.neighbors import NearestNeighbors
import test_recommender


# Flask related stuff
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def database_connection():
    conn = psycopg2.connect(database="movie_rec", user="admin",
                            password="admin", host="movie_database", port="5432")
    return conn


def load_data():
    conn = database_connection()
    cursor = conn.cursor()
    # cursor.execute(
    #     "SELECT m.primarytitle, m.titletype, r.votes, r.averagerating FROM movie_table m, rating_table r where "
    #     "r.tconst = m.tconst;")
    cursor.execute(
        "SELECT user_id, movie_id, rating FROM rating_table")
    rating_data = cursor.fetchall()
    ratings = pd.DataFrame(rating_data)
    ratings.rename(
        columns={0: 'user_id', 1: 'movie_id', 2: 'rating'}, inplace=True)
    ratings = ratings.apply(pd.to_numeric)
    cursor.execute(
        "SELECT id, title FROM movie_table")
    movies_data = cursor.fetchall()
    movies = pd.DataFrame(movies_data)
    movies.rename(columns={0: 'id', 1: 'title'}, inplace=True)
    conn.commit()
    print("Data loaded successfully")
    return ratings, movies


def get_movie_id(movie_name, tconst = False):
    conn = database_connection()
    cursor = conn.cursor()
    if tconst:
        cursor.execute(
            " SELECT id FROM movie_table WHERE imdb_id = '" + movie_name + "' ")
        movie_id = cursor.fetchall()
        if len(movie_id) > 0:
            m_id = movie_id[0][0]
        else:
            return 0
    else:        
        movie_name = movie_name.replace("'", "''")
        cursor.execute(
            " SELECT id FROM movie_table WHERE title = '" + movie_name + "' ")
        movie_id = cursor.fetchall()
        if len(movie_id) > 0:
            m_id = movie_id[0][0]
        else:
            return 0
    return m_id


def create_X(df):
    """
    Generates a sparse matrix from ratings dataframe.

    Args:
        df: pandas dataframe containing 3 columns (userId, movieId, rating)

    Returns:
        X: sparse matrix
        user_mapper: dict that maps user id's to user indices
        user_inv_mapper: dict that maps user indices to user id's
        movie_mapper: dict that maps movie id's to movie indices
        movie_inv_mapper: dict that maps movie indices to movie id's
    """
    M = df['user_id'].nunique()
    N = df['movie_id'].nunique()

    user_mapper = dict(zip(np.unique(df["user_id"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movie_id"]), list(range(N))))

    user_inv_mapper = dict(zip(list(range(M)), np.unique(df["user_id"])))
    movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movie_id"])))

    user_index = [user_mapper[i] for i in df['user_id']]
    item_index = [movie_mapper[i] for i in df['movie_id']]

    X = csr_matrix((df["rating"], (user_index, item_index)), shape=(M, N))

    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper


def find_similar_movies(movie_id, X, movie_mapper, movie_inv_mapper, k, metric='cosine'):
    """
    Finds k-nearest neighbours for a given movie id.

    Args:
        movie_id: id of the movie of interest
        X: user-item utility matrix
        k: number of similar movies to retrieve
        metric: distance metric for kNN calculations

    Output: returns list of k similar movie ID's
    """
    X = X.T
    neighbour_ids = []

    movie_ind = movie_mapper[movie_id]
    movie_vec = X[movie_ind]
    if isinstance(movie_vec, (np.ndarray)):
        movie_vec = movie_vec.reshape(1, -1)
    # use k+1 since kNN output includes the movieId of interest
    kNN = NearestNeighbors(n_neighbors=k+1, algorithm="brute", metric=metric)
    kNN.fit(X)
    neighbour = kNN.kneighbors(movie_vec, return_distance=False)
    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(movie_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids


def recommend(movie_id):
    if movie_id == 0:
        return ["failed"]
    rating, movie = load_data()
    print(rating.dtypes)
    print(movie.dtypes)
    X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(
        rating)

    movie_titles = dict(zip(movie['id'], movie['title']))

    similar_movies = find_similar_movies(
        movie_id, X, movie_mapper, movie_inv_mapper, metric='cosine', k=10)
    movie_title = movie_titles[movie_id]

    # print(f"Because you watched {movie_title}:")
    recommended_movie = []
    for i in similar_movies:
        recommended_movie.append(movie_titles[i])
    return recommended_movie


# function to get recommendation from database
@app.route("/get-recommendation/<movie>", methods=['GET'])
@cross_origin()
def get_recommendation(movie):
    recommended_movies = recommend(get_movie_id(clean_request(movie)))
    print("recieved request for ", movie)
    return ",".join(recommended_movies)

# function to get recommendation from database
@app.route("/get-recommendation/id/<tconst>", methods=['GET'])
@cross_origin()
def get_recommendation_id(tconst):
    imdb_id = str(int(tconst[2:]))
    recommended_movies = recommend(get_movie_id(imdb_id, True))
    print("recieved request for ", imdb_id)
    movies = ",".join(recommended_movies)
    return jsonify({"res": "success", "movies":movies}) 


# check if application is running
@app.route("/api/check-status", methods=['GET'])
def check_status():
    return jsonify({"status": "success"})


def clean_request(movie):
    if (movie.find("%20")):
        movie = movie.replace("%20", " ")
    return movie


if __name__ == '__main__':
    print("======================  RUNNING UNIT TESTS (Recommender) ====================== ")
    if test_recommender.unit_test():
        print("======================  UNIT TESTS PASSED (Recommender) ====================== ")
        print("Starting Recommender Microservice")
        app.run(host='0.0.0.0', port=2211, debug=True)
    else:
        print("======================  UNIT TESTS FAILED (Recommender) ====================== ")

