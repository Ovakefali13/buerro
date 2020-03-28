
function getCurrentLocation(callback) {
    //Dummy one, which will result in a working next statement.
    navigator.geolocation.getCurrentPosition(function () {}, function () {}, {});
    navigator.geolocation.getCurrentPosition(pos => {
        if(typeof pos == 'undefined') {
            callback(null, "could not determine geolocation")
        }
        console.log('succ', pos)
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        callback( [ lat, lon ], undefined );
    }, err => {
        callback( null, err );
    },
    {
        timeout: 5000,
        enableHighAccuracy: true
    });
}
            

function sendCurrentLocation() {
    console.log('Sending...');
    getCurrentLocation((location, err) => {
        if(err) {
            console.error(err)
            return
        }

        return fetch('api/location', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                    'location': location 
                })
            })

        .then(function(response) {
            if (!response.ok) {
              console.error(response.json())
              throw new Error('Bad status code from server.');
            }

            return response.json();
        })
        .then(function(responseData) {
            if (!(responseData.success)) {
              throw new Error('Bad response from server.');
            }
        });

    });
}
