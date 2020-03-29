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

function subscribeUser() {

    const subscribeOptions = {
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(
            "BMMA-CffOzTP-pSgzGqrgISf1hKXs9rgELQU1NZmq-_G7aeSiZktA68GdJtlEkKOwMaazkXFolRW8uBRpPKOexA"
        )
    }

    return swRegistration.pushManager.subscribe(subscribeOptions);
}

if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {

        navigator.serviceWorker.register('/js/service-worker.js')
        .then((registration) => {
            console.log('ServiceWorker registration successful: ', registration);
            swRegistration = registration
            return registration.pushManager.getSubscription()
        }, err => {
            console.error(err);
        })
        .then((pushSubscription) => {
            if(pushSubscription !== null) {
                console.log('User is subscribed.');
                sendSubscriptionToBackEnd(pushSubscription)
                .then(() => { 
                    console.log('Successfully sent pushSubscription to backend');
                    isSubscribed = true
                })
                .catch((err) => {
                    console.error('Failed to send subscription: ', err);
                    pushSubscription.unsubscribe();
                    isSubscribed = false;
                });
            } else {
                console.log('User is not subscribed.');
                subscribeUser()
                .then((pushSubscription) => sendSubscriptionToBackEnd(pushSubscription))
                .then(() => { 
                    console.log('Successfully sent pushSubscription to backend');
                    isSubscribed = true
                })
                .catch((err) => {
                    console.error('Failed to send subscription: ', err);
                    pushSubscription.unsubscribe();
                    isSubscribed = false;
                });
            }
        }, err => {
            console.error(err);
        });
    });

}

function sendSubscriptionToBackEnd(subscription) {
  return fetch('/api/save-subscription', {
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

    putBotMessage("Hello, it's me, the PDA for your buerro. Ask me anything.")

    $('#submit-btn').prop('disabled',true);
    $("#submit-btn").click(function () {        
        stop_record()        
        processUserPrompt($("#prompt_input").val());        
        $('#loader').show(100);
        $('#submit-btn').val('Loading');
        $('#submit-btn').prop('disabled',true);
        $("#prompt_input").val("");
        //$("#prompt_input").focus()
    });
    
    $("#prompt_input").on('change input', function() {
        if (!$.trim($("#prompt_input").val())) {
            $('#submit-btn').prop('disabled', true)
        } else {
            $('#submit-btn').prop('disabled', false)
        }
    })

    navigator.serviceWorker.addEventListener('message', event => {
    if(event.data.options.data) {
        if(event.data.options.data.message) {
            putBotMessage(event.data.options.data.message);
        }
    }
});
})

function putUserMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(false, message));

    container[0].scrollTop = container[0].scrollHeight
}

function putBotMessage(message) {
    var container = $(".bubblecontainer")
    $('#submit-btn').val('Send');
    $('#loader').hide(100);
    container.append(generateChatBubble(true, message));
    speak();
    container[0].scrollTop = container[0].scrollHeight
}


function processUserPrompt(prompt) {
    //Send to backend with async promise or something
    putUserMessage(prompt);
    getCurrentLocation(location => {
        return fetch('/api/message', {
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
              putBotMessage("Server communication failed.");
            }

            return response.json();
        })
        .then(function(responseData) {
            if (!(responseData.success && responseData.data)) {
              throw new Error('Bad response from server.');
              putBotMessage("Server communication failed.");
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
