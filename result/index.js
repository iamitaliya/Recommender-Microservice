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
    app.listen(8080);
}
openPort(app);

// get movie names from database and store it somewher to autocomplete