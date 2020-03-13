BACKEND_HOST = "http://localhost:9150"
notificationOptions = {
    'lang': 'de',
    //'body': 
    //'data':
    //'icon':
    //'vibrate':
    'requireInteraction': false,
    'renotify': true,
    'silent': false
}

function notify(message, body, vibrate) {
    if("Notification" in window) {
        var options = {
          'body': body,
          'vibrate': vibrate 
        }
        if(Notification.permission === "granted") {
            var n = new Notification(message,options);
        } else if(Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if(permission === "granted") {
                    var notification = new Notification(message, options);
                }
            })
        }
    }
}

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

swRegistration = null;

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
                subscribeUser();
            }
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
    if (!(responseData.data && responseData.data.success)) {
      throw new Error('Bad response from server.');
    }
  });
}


$(document).ready(function() {
    subscribed = false

    $(".chatcontainer").append(generateChatBubble(true, "Hello its me the bot"));
    $(".chatcontainer").append(generateChatBubble(false, "Hello its me the user"));

    $("#prompt_input").keypress(function(e) {
        if(e.which == 13) {
            if(!subscribed) {
                subscribeToPushNotifications();
            }
            processUserPrompt($("#prompt_input").val());
            $("#prompt_input").val("");
        }
    });

    $("#submit-btn").click(function () {
        processUserPrompt($("#prompt_input").val());
        $("#prompt_input").val("");
    });
})


function processUserPrompt(prompt) {
    //Send to backend with async promise or something
    $(".chatcontainer").append(generateChatBubble(false, prompt));
    $(".chatcontainer").append(generateChatBubble(true, "Warning! No backend connected"));
}


function generateChatBubble(bot, text) {
    if(bot) {
        return "<div class='card bubble bubble-bot'><div class='card-body'>" + text + "</div></div>";
    } else {
        return "<div class='card bubble bubble-user'><div class='card-body'>" + text + "</div></div>";
    }
}
