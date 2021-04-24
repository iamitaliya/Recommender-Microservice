var express = require('express');
var app = express();
var path = require('path');
var fs = require('fs');

function openPort(app) {
    app.use("/static", express.static('./static/'));
    // app.use(express.static(path.join(__dirname, '/result')));
    app.get('/', function (req, res) {
        res.sendFile(path.join(__dirname + '/index.html'));
    });
    app.listen(2411);
}

const { Client } = require('pg');
const { json } = require('express');
const client = new Client({
    user: "admin",
    password: "admin",
    host: "movie_database",
    port: 2311,
    database: "movie_rec"
})

execute(app);

async function execute(app) {
    try {
        openPort(app)
        await client.connect()
        console.log("Connected successfully")
        movies = await client.query("select title from movie_table")
        console.log(movies)
        // bar_data = toRows(movies.rows, movies.rowCount)
        var arr1 = new Array()
        for (let i = 0; i < movies.rowCount; i++) {
            arr1.push(Object.values(movies.rows[i]))
        }
        arr1 = [].concat.apply([], arr1)
        toJS(arr1)
        // console.log(arr1)
        await client.end()
        console.log("Client disconnected")
    }
    catch (ex) {
        console.log("Error : " + ex)
    }
    finally {
        client.end()
        console.log("client disconnected")
    }
}


function toJS(data) {

    fs.writeFile(__dirname + "/static/movies.json", JSON.stringify(data), function (err) {
        if (err) {
            console.log(err)
        } else {
            console.log(" JSON file created")
        }
    })

}


// get movie names from database and store it somewher to autocomplete