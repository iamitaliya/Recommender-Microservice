from datetime import datetime, time
from types import ClassMethodDescriptorType
from flask import Flask, json, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
import wget
import zipfile
import os
import psycopg2
import multiprocessing
app = Flask('__name__')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
PASSWORD = "MOVIES"
processing = False

def API(Conf):
    print('In API selction')
    app.run(host='0.0.0.0', port=2111)

host = 'movie_database'
# Connect to postgres sql database
def database_connection():
    conn = psycopg2.connect(database="movie_rec", user="admin",
                            password="admin", host="movie_database", port="5432")
    return conn


def create_tables():
    conn = database_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS movie_table
             (id INT PRIMARY KEY     NOT NULL,
             title         TEXT    NOT NULL,
             imdb_id TEXT
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
    with open("/".join([path, raw_data.split(".")[0], "links.csv"]), "r") as links_file:
        links_data = pd.read_csv(links_file, header=0)
    if os.path.exists(raw_data):
        os.remove(raw_data)
        print("file removed")
    return [movies_data, ratings_data, tags_data, links_data]


def remove_na(data):
    data.dropna(axis=0, inplace=True)
    return data


def remove_duplicates(data):
    data.drop_duplicates(inplace=True)
    return data


def load_tables(movies, m_ratings, links):
    movies = remove_na(movies)
    movies = remove_duplicates(movies)
    m_ratings = remove_na(m_ratings)
    movies = movies.merge(links, on='movieId')
    # cleaning data
    new_title = []
    for item in movies['title']:
        if ", The" in item:
            new_movie = item.replace(", The", "").strip()
            new_title.append("The " + new_movie)
        else:
            new_title.append(item.strip())
    movies['title'] = new_title
    print(movies)
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("""DELETE FROM movie_table""")
    for row in movies.itertuples():
        mov_id = int(row.movieId)
        title = row.title
        imdb_id = row.imdbId
        cur.execute("""
            INSERT INTO movie_table
            VALUES (%s, %s, %s);
            """, (mov_id, title, imdb_id))
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


# check if application is running
@app.route("/api/check-status", methods=['GET'])
def check_status():
    return jsonify({"status": "success"})

# function to clean data
@app.route("/api/load-data/<password>", methods=['GET', 'POST'])
def clean_data(password):
    global processing
    if not processing:
        processing = True
        try:
            if password == PASSWORD:
                print("Data loading process started")
                url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
                movies, ratings, tags, links = data_download(url)
                create_tables()
                load_tables(movies, ratings, links)

                print("Data loaded successfully")
                processing = False
                return jsonify({"status": "success"})
            else:
                print("Wrong password")
                processing = False
                return jsonify({"status": "Invalid Password"})
        except:
            processing = False
            return jsonify({"status": "Internal Error"})
    else:
        return jsonify({"status": "Wait for process to finish"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2111, debug=True)
