BACKEND_HOST = "http://localhost:9150"

swRegistration = null;

/**
 * urlBase64ToUint8Array
 *
 * @param {string} base64String a public vavid key
 */
function urlBase64ToUint8Array(base64String) {
    var padding = '='.repeat((4 - base64String.length % 4) % 4);
    var base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    var rawData = window.atob(base64);
    var outputArray = new Uint8Array(rawData.length);

    for (var i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

navigator.serviceWorker.addEventListener('message', event => {
    if(event.data.options.data) {
        if(event.data.options.data.message) {
            putBotMessage(event.data.options.data.message);
        }
    }
});


function subscribeUser() {

    const subscribeOptions = {
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(
            "BMMA-CffOzTP-pSgzGqrgISf1hKXs9rgELQU1NZmq-_G7aeSiZktA68GdJtlEkKOwMaazkXFolRW8uBRpPKOexA"
        )
    }

    swRegistration.pushManager.subscribe(subscribeOptions)
    .then(pushSubscription => {
        console.log('Received PushSubscription: ', pushSubscription); 
        try {
            sendSubscriptionToBackEnd(pushSubscription);
            console.log('Successfully sent subscription to backend');
            isSubscribed = true;
        } catch(err) {
            console.error(err);
            pushSubscription.unsubscribe();
        }
    });
}

if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {

        navigator.serviceWorker.register('/service-worker.js')
        .then((registration) => {
            console.log('ServiceWorker registration successful: ', registration);
            swRegistration = registration
            return registration.pushManager.getSubscription()
        }, err => {
            console.error(err);
        })
        .then((subscription) => {
            isSubscribed = !(subscription === null)
            if(isSubscribed) {
                console.log('User is subscribed.');
            } else {
                console.log('User is not subscribed.');
                subscribeUser(); }
        }, err => {
            console.error(err);
        });
    });

}


function sendSubscriptionToBackEnd(subscription) {
  return fetch(BACKEND_HOST+'/save-subscription', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(subscription)
  })
  .then(function(response) {
    if (!response.ok) {
      console.error(response.json())
      throw new Error('Bad status code from server.');
    }

    return response.json();
  })
  .then(function(responseData) {
    if (!responseData.success) {
      throw new Error('Bad response from server.');
    }
  });
}

$(document).ready(function() {
    sendCurrentLocation();
    var minutes = 5
    setInterval(() => {
        sendCurrentLocation();
    }, 1000 * 60 * minutes)  

    $(".bubblecontainer").append(generateChatBubble(true, "Hello its me the bot"));
    $(".bubblecontainer").append(generateChatBubble(false, "Hello its me the user"));

    $("#prompt_input").keypress(function(e) {
        if(e.which == 13) {
            processUserPrompt($("#prompt_input").val());
            $("#prompt_input").val("");
        }
    });

    $("#submit-btn").click(function () {
        processUserPrompt($("#prompt_input").val());
        $("#prompt_input").val("");
    });
})

function putUserMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(false, message));

    container[0].scrollTop = container[0].scrollHeight
}

function putBotMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(true, message));

    container[0].scrollTop = container[0].scrollHeight
}


function processUserPrompt(prompt) {
    //Send to backend with async promise or something
    putUserMessage(prompt);
    getCurrentLocation(location => {
        return fetch(BACKEND_HOST+'/message', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                   message: prompt,
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
            if (!(responseData.success && responseData.data)) {
              throw new Error('Bad response from server.');
            }

            putBotMessage(responseData.data.message);
        });
    });
}


function generateChatBubble(bot, text) {
    if(bot) {
        return "<div class='card bubble bubble-bot'><div class='card-body'>" + text + "</div></div>";
    } else {
        return "<div class='card bubble bubble-user'><div class='card-body'>" + text + "</div></div>";
    }
}

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

        return fetch(BACKEND_HOST+'/location', {
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
