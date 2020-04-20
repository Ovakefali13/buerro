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

/*
function pubKeyFromPem(pem) {
    const start = "-----BEGIN PUBLIC KEY-----"
    const end = "-----END PUBLIC KEY-----"

    console.log(pem)

    var key = pem.substring( // get key in between start, end
        pem.indexOf(start) + start.length + 1,
        pem.indexOf(end),
    );

    key = key.replace(/(\r\n|\n|\r)/gm, ""); // replace line breaks
    return key;
}
*/

function getAppServerKey() {
    return fetch('/sec/app-server-key', {
      method: 'GET',
    })
    .then(async (response) => {
      const key = await response.text();
      if(key.length < 1) {
        throw new Error("Failed to get app server key");
      }
      return key;
    });
}

function subscribeUser() {

  return getAppServerKey()
  .then(key => {
    console.log('Key: ', key)
    const subscribeOptions = {
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(key)
    }

    return swRegistration.pushManager.subscribe(subscribeOptions);
  });
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
                sendSubscriptionToBackEnd(pushSubscription)
                .then(() => {
                    isSubscribed = true
                })
                .catch((err) => {
                    console.error('Failed to send subscription: ', err);
                    pushSubscription.unsubscribe();
                    isSubscribed = false;
                });
            } else {
                subscribeUser()
                .then((pushSubscription) => sendSubscriptionToBackEnd(pushSubscription))
                .then(() => {
                    console.log('Successfully sent pushSubscription to backend');
                    isSubscribed = true
                })
                .catch((err) => {
                    console.error('Failed to send subscription: ', err);
                    if(pushSubscription) {
                        pushSubscription.unsubscribe();
                    }
                    isSubscribed = false;
                });
            }
        })
        .catch(err => {
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
  })
  .catch(err => {
    console.error('Error sending subscripton to backend: ', err);
  });
}
