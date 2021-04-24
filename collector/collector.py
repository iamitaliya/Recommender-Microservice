from datetime import datetime, time
import pandas as pd
import wget
import zipfile
import os
import psycopg2
import flask
import multiprocessing
app = flask.Flask('__name__')


def API(Conf):
    print('In API selction')
    app.run(host='0.0.0.0', port=2111)


# Connect to postgres sql database
def database_connection():
    conn = psycopg2.connect(database="movie_rec", user="admin",
                            password="admin", host="movie_database", port="2311")
    return conn


def create_tables():
    conn = database_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS movie_table
             (id INT PRIMARY KEY     NOT NULL,
             title         TEXT    NOT NULL
             );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS movie_map_table
             (id INT PRIMARY KEY     NOT NULL,
             mapper    INT    NOT NULL
             );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS movie_inv_map_table
             (inv_id INT PRIMARY KEY     NOT NULL,
             inv_mapper    INT    NOT NULL
             );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS rating_table
             (id INT PRIMARY KEY     NOT NULL,
             user_id  INT,
             movie_id  INT,
             rating  TEXT 
             );""")
    conn.commit()
    cursor.execute(
        """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rating_table'""")
    is_table = cursor.fetchall()
    print("rating_table created successfully in PostgreSQL ")
    conn.close()
    return is_table

# data downloading
# data cleaning
# data send to database


def data_download(url):
    print("Downloading data")
    raw_data = wget.download(url)
    print("Download finished")
    path = "collector/data"
    with zipfile.ZipFile(raw_data, "r") as f:
        f.extractall(path)
    with open("/".join([path, raw_data.split(".")[0], "movies.csv"]), "rb") as movies_file:
        movies_data = pd.read_csv(movies_file, header=0, encoding="utf-8")
    with open("/".join([path, raw_data.split(".")[0], "ratings.csv"]), "r") as ratings_file:
        ratings_data = pd.read_csv(ratings_file, header=0)
    with open("/".join([path, raw_data.split(".")[0], "tags.csv"]), "r") as tags_file:
        tags_data = pd.read_csv(tags_file, header=0)
    if os.path.exists(raw_data):
        os.remove(raw_data)
        print("file removed")
    return [movies_data, ratings_data, tags_data]


def data_cleaning(data):
    return pd.DataFrame(data)


def load_tables(movies, m_ratings):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("""DELETE FROM movie_table""")
    for row in movies.itertuples():
        mov_id = int(row.movieId)
        title = row.title
        cur.execute("""
            INSERT INTO movie_table
            VALUES (%s, %s);
            """, (mov_id, title))
    cur.execute("""DELETE FROM rating_table""")
    id_r = 0
    for row in m_ratings.itertuples():
        use_id = int(row.userId)
        movi_id = int(row.movieId)
        rating = row.rating
        cur.execute("""
            INSERT INTO rating_table
            VALUES (%s, %s, %s, %s);
            """, (id_r, use_id, movi_id, rating))
        id_r += 1
    conn.commit()
    print("table loaded successfully")


if __name__ == "__main__":
    config = {"Something": "SomethingElese"}
    p = multiprocessing.Process(target=API, args=(config))
    p.start()
    print("Server Started")

    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    movies, ratings, tags = data_download(url)
    t1 = datetime.now()
    create_tables()
    load_tables(movies, ratings)
    t2 = datetime.now()
    print("Time taken", t2 - t1)

    p.terminate()
    p.join()
    print("Server Stopped")
