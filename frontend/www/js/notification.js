swRegistration = null;

var md_converter = undefined;
try {
    var md_converter = new showdown.Converter();
} catch (e) {
    if (!e instanceof ReferenceError) {
        throw e;
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
        .catch(err => {
            throw new Error('Failed to register service worker: ' + err.message);
        })
        .then((registration) => {
            console.log('ServiceWorker registration successful: ', registration);
            swRegistration = registration
            try {
                return registration.pushManager.getSubscription()
            } catch(err) {
                throw new Error("Failed to register push subscription: " + err.message);
            }
        })
        .then((pushSubscription) => {
            if(pushSubscription !== null) {
                sendSubscriptionToBackEnd(pushSubscription)
                .then(() => {
                    isSubscribed = true
                })
                .catch((err) => {
                    pushSubscription.unsubscribe();
                    isSubscribed = false;
                    throw new Error('Failed to send subscription: ' + err.message);
                });
            } else {
                subscribeUser()
                .then((pushSubscription) => sendSubscriptionToBackEnd(pushSubscription))
                .then(() => {
                    console.log('Successfully sent pushSubscription to backend');
                    isSubscribed = true
                })
                .catch((err) => {
                    if(pushSubscription) {
                        pushSubscription.unsubscribe();
                    }
                    isSubscribed = false;
                    throw new Error('Failed to send subscription: ' + err.message);
                });
            }
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
  .then(async (response) => {
    if (!response.ok) {
      message = undefined
      try {
          resp = await response.json()
          message = resp.error.message;
      } catch(e) {}
      if(message) {
          throw new Error('Bad server response: ', message);
      } else {
          throw new Error('Bad status code from server.');
      }
    }

    return response.json();
  })
  .then(function(responseData) {
    if (!responseData.success) {
        throw new Error('Bad response from server.');
    }
  });
}
