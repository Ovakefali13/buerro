
const express = require('express');
const server = express();

server.use(express.static('www'));

server.get("/", (req, res) => {
   res.sendFile(__dirname + '/index.html');
});

const port = 4000

server.listen(port, () => {
    console.log(`Frontend Server listening at ${port}`);
});
