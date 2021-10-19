var express = require('express');
var app = express();
var path = require('path');
var fs = require('fs');
var fetch = require('node-fetch')
app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });

function openPort(app) {
    app.use("/static", express.static('./static/'));
    // app.use(express.static(path.join(__dirname, '/result')));
    app.get('/', function (req, res) {
        res.sendFile(path.join(__dirname + '/index.html'));
    });

    app.get('/api/check-status', async function(req, res){
        try {
            res.send(JSON.stringify({status : "success"}))
        }
        catch(err) {
            console.log(err)
            res.send(JSON.stringify({res : "error retriving status"}))
        }
    })


    app.listen(2411);
    }
    
    const { Client } = require('pg');
    const { json } = require('express');
    const client = new Client({
        user: "admin",
        password: "admin",
        host: "movie_database",
        port: 5432,
        database: "movie_rec"
    })
    

loadData().then(() => {
    execute(app)}).catch(err => {
        console.log(err)
    })

async function loadData() {
    try {
        const result = await fetch("http://collector:2111/api/load-data/MOVIES").then(response => response.json()).then(data => {
            console.log(data)
            if (data.status === "success") {
                console.log("data loaded")
            } else {
                console.log("data not loaded")
            }
        }).catch(err => {   
            console.log(err)
        })
        return result
    }
    catch (ex) {
        console.log(ex)
    }
}

async function execute(app) {
    try {
        openPort(app)
        await client.connect()
        console.log("Connected successfully")
        movies = await client.query("select title from movie_table")
        // bar_data = toRows(movies.rows, movies.rowCount)
        var arr1 = new Array()
        for (let i = 0; i < movies.rowCount; i++) {
            arr1.push(Object.values(movies.rows[i]))
        }
        arr1 = [].concat.apply([], arr1)
        toJSON(arr1)
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


function toJSON(data) {
    fs.writeFile(__dirname + "/static/movies.json", JSON.stringify(data), function (err) {
        if (err) {
            console.log(err)
        } else {
            console.log(" JSON file created")
            return true
        }
        return false
    })


}

module.exports = toJSON;
// get movie names from database and store it somewher to autocomplete