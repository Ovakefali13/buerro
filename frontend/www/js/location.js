
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
            console.log('Failed to get location: ', err);
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
    .catch(err => {
        console.error('Failed to send location because it could not be acquired');
        return
    })
    .then(location => {
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
          resp = undefined
          try {
              resp = response.json().error.message;
          } catch {}
          if(resp) {
              throw new Error('Bad server response: ', resp);
          } else {
              throw new Error('Bad status code from server.');
          }
        }

        return response.json();
    })
    .then(function(responseData) {
        if (!(responseData.success)) {
          throw new Error('Bad response from server.');
        }
    });
}

