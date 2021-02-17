import pandas as pd
import wget
import gzip
import zipfile
import os
import psycopg2
import flask
import multiprocessing


# app = flask.Flask('__name__')


# def API(Conf):
#     print('In API selction')
#     app.run(host='0.0.0.0', port=2111)

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


url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
movies, ratings, tags = data_download(url)

movies['genres'] = movies['genres'].apply(lambda x: x.split("|"))
