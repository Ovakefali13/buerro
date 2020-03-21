
const express = require('express');
const app = express();
const https = require('https');
const fs = require('fs');

const port = 4000

app.use(express.static('www'));

app.get("/", (req, res) => {
   res.sendFile(__dirname + '/index.html');
});

const httpsOptions = {
    key: fs.readFileSync('./ssl/device.key'),
    cert: fs.readFileSync('./ssl/localhost.crt')
}

const server = https.createServer(httpsOptions, app).listen(port, () => {
    console.log(`Frontend Server listening at ${port}`);
});

