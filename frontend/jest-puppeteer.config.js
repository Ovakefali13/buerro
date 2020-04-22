// jest-puppeteer.config.js
port = 4444;
if(process.env.FRONTEND_PORT) {
    port = process.env.FRONTEND_PORT;
}
console.log('Test Server running on port ', port);

module.exports = {
  server: {
    command: 'node server.js',
    port: port,
  },
}
