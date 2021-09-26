const toJSON = require('./server')
const fs = require('fs')
const path = __dirname + "/static/movies.json"

const data = [1, 2, 3]

test("Testing toJS method", () => {
    expect(toJSON(data))
})
