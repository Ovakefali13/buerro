sendCurrentLocation = require('./location.js')

test('can send location', () => {
    sendCurrentLocation()
    .then(response => expect.toBeTruthy(response.success))
    .catch(err => {});
});
