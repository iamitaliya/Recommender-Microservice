from flask import Flask, json, jsonify, request
from flask_cors import CORS, cross_origin
import psycopg2


# Flask related stuff
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# function to get recommendation from database
@app.route("/get-recommendation/<movie>", methods=['GET'])
@cross_origin()
def get_recommendation(movie):
    recommended_movies = []
    print("recieved request for ", movie)
    # TODO: get movie names and cobine it to a string with "," seperator
    return ("movie1,movie2," + movie)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2211, debug=True)

# TODO:
# start a server to recieve requests
# take the data from database to process request
# process the request
# send result back to request
