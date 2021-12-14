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
    
const { Pool } = require('pg');
const { json } = require('express');
const client = new Pool({
    user: "admin",
    password: "admin",
    host: "movie_database",
    port: 5432,
    database: "movie_rec"
})
    

loadData()

async function loadData() {
    try {
        // ------------------Integration testing--------------------------
        // check status of required microservices
        console.log("---------------------------- INTEGRATION TESTING STARTED --------------------------")
        const services = { collector : "http://collector:2111/api/check-status",
                           recommender : "http://recommender:2211/api/check-status",
                           dashboard : "http://dashboard:5555/api/check-status",
                           database : "visualiser database"
                            }
        const res_services = {}
        for(const [service, url] of Object.entries(services))
        {
            if(service == "database")
            {
                res_services[service] = await check_db("select 2 + 2 as count")
            }else{
                res_services[service] = await check_status(url)
            }
            console.log(service + ": " + (res_services[service] ? "PASSED"  : "FAILED") )
        }
        const all_passed = Object.values(res_services).every(Boolean)
        if(!all_passed){
            return integration_failed()
        }
        // check if there is data already available in database
        console.log("Checking data in database")
        var query = "select count(*) from movie_table"
        const table_rows = await check_db(query)
        var data_found = false
        
        if(table_rows < 5){
            console.log("No data found! \nLoading the data... \nThis will take around 5 minutes...")
            // if there is no data then, get the data
            const result = await fetch("http://collector:2111/api/load-data/MOVIES").then(response => response.json()).then(data => {
                if (data.status === "success") {
                    console.log("Data loaded successfully")
                    data_found = false
                } else {
                    console.log("Data loading failed")
                }
            }).catch(err => {   
                // console.log(err)
                console.log("Data loading failed")
            })
        }else{
            data_found = true
        }

        // passing dummy data to see if we have data
        fetch('http://recommender:2211/get-recommendation/Iron%20Man%20(2008)').then(function (response) {
            // The API call was successful!
            return response.text();
        }).then(function (html) {
            // This is the HTML from our response as a text string
            if(html.length > 2){
                return integration_passed(data_found)
            }else{
                return integration_failed()
            }
        }).catch(function (err) {
            // There was an error
            return integration_failed(err)
        });
    }
    catch (ex) {
        return integration_failed(err)
    }
}

function integration_failed(err = 0){
    // console.log(err)
    console.log("Error occured while testing.\n---------------------------- INTEGRATION TESTING ENDED -------------------------- \nStopping the Service.")
}
function integration_passed(data_found){
    console.log("Integration Test Passed.\n ---------------------------- INTEGRATION TESTING ENDED -------------------------- \nStarting the Service.")
    execute(app).catch(err => {
        console.log(err)
    })
    if(data_found){
        console.log("Data already available... \nUpdating the database")
        fetch("http://vis_collector:4321/api/load-data/MOVIES").then(response => response.json()).then(data => {
            if (data.status === "success") {
                console.log("Data loaded successfully")
                execute(app, true)
            } else {
                console.log("Data loading failed")
            }
        }).catch(err => {   
            // console.log(err)
            console.log("Data loading failed")
        })
    }
}

async function check_db(query){
    return client.query(query).then(function (result) {
        return result.rows[0]['count']
    }).catch(err => {
        // console.log(err) 
        return 0
    })
}

// to check status of microservices
async function check_status(url)
{
    return fetch(url).then(response => response.json()).then(res => {
    if(res.status == "success"){ 
        return true
    }else{
        return false
    }
    }).catch((error) => {
        return false
    })
}


async function execute(app, port_opened=false) {
    try {
        if (!port_opened){
            openPort(app)
        }
        await client.connect()
        // console.log("Connected successfully")
        movies = await client.query("select title from movie_table")
        // bar_data = toRows(movies.rows, movies.rowCount)
        var arr1 = new Array()
        for (let i = 0; i < movies.rowCount; i++) {
            arr1.push(Object.values(movies.rows[i]))
        }
        arr1 = [].concat.apply([], arr1)
        toJSON(arr1)
        // console.log("Client disconnected")
    }
    catch (ex) {
        console.log("Error : " + ex)
    }
    finally {
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