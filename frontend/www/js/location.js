
function getCurrentLocation() {

    return new Promise((resolve, reject) => {
        //Dummy one, which will result in a working next statement.
        navigator.geolocation.getCurrentPosition(function () {}, function () {}, {});
        navigator.geolocation.getCurrentPosition(pos => {
            if(typeof pos == 'undefined') {
                reject("could not determine geolocation")
            }

            var lat = pos.coords.latitude;
            var lon = pos.coords.longitude;
            resolve([ lat, lon ]);
        }, err => {
            reject(err);
        },
        {
            timeout: 5000,
            enableHighAccuracy: true
        });
    });
}

function sendCurrentLocation() {
    console.log('Sending...');

    return getCurrentLocation()
    .then(() => {

        return fetch('api/location', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                    'location': location
                })
            })
    })
    .then(async (response) => {
        if (!response.ok) {
          resp = await response.json()
          console.error('Error: ', resp.error.message);
          throw new Error('Bad status code from server.');
        }

        return response.json();
    })
    .then(function(responseData) {
        if (!(responseData.success)) {
          throw new Error('Bad response from server.');
        }
    });
}

