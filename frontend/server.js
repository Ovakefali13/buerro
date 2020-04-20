const HTTPS=false

const express = require('express');
const app = express();
const https = require('https');
const fs = require('fs');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

var port = 4000;
if(process.env.FRONTEND_PORT) {
    port = process.env.FRONTEND_PORT;
}

var backend_api = "http://localhost";
var backend_port = 9150;
if(process.env.BACKEND_PORT) {
    backend_port = process.env.BACKEND_PORT;
}
const backend = backend_api + ':' + backend_port;

app.use("/", express.static('www'));

app.use("/sec/app-server-key", express.static(path.join(__dirname, '..', 'sec', 'app_server_key.pem')));

app.use('/scripts', express.static(path.join(__dirname, '/node_modules/bootstrap/dist/')));
app.use('/scripts', express.static(path.join(__dirname, '/node_modules/jquery/dist/')));
app.use('/scripts', express.static(path.join(__dirname, '/node_modules/showdown/dist/')));

// proxy middleware options
const options = {
  target: backend, // target host
  //changeOrigin: true, // needed for virtual hosted sites
  pathRewrite: {'^/api' : ''}
};

// create the proxy (without context)
const exampleProxy = createProxyMiddleware(options);
app.use('/api', exampleProxy);

if(HTTPS) {

    const httpsOptions = {
        key: fs.readFileSync('./ssl/device.key'),
        cert: fs.readFileSync('./ssl/localhost.crt')
    }

    const server = https.createServer(httpsOptions, app).listen(port, () => {
        console.log(`Frontend Server listening at ${port}`);
    });
} else {
    app.listen(port, () => {
        console.log(`Frontend Server listening at ${port}`);
    });
}
