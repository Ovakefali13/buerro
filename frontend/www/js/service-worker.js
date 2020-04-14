self.addEventListener('push', async function(event) {
    console.log('[Service Worker] Push Received.');
    console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);

    var options = {
        icon:  '/ico/android-chrome-192x192.png',
        badge: '/ico/favicon-32x32.png'
    };

    try {
        data = event.data.json();
        title = data.title;

        options = Object.assign({}, data.options, options);
    } catch(e) {
        title = event.data.text();
    }

    self.registration.showNotification(title, options);

    // find the client(s) you want to send messages to:
    self.clients.matchAll({includeUncontrolled: true, type: 'window'}).then( (clients) => {
        if (clients && clients.length) {
            // you need to decide which clients you want to send the message to..
            const client = clients[0];
            client.postMessage({title: title, options: options});
        }
    });
});

/*
function isClientFocused() {
  return clients.matchAll({
    type: 'window',
    includeUncontrolled: true
  })
  .then((windowClients) => {
    let clientIsFocused = false;

    for (let i = 0; i < windowClients.length; i++) {
      const windowClient = windowClients[i];
      if (windowClient.focused) {
        clientIsFocused = true;
        break;
      }
    }

    return clientIsFocused;
  });
}

self.addEventListener('notificationclick', function(event) {
  const promiseChain = isClientFocused()
  .then((clientIsFocused) => {
    if (clientIsFocused) {
      console.log('Don\'t need to show a notification.');
      return;

    }

    // Client isn't focused, we need to show a notification.
    return self.registration.showNotification('Had to show a notification.');
  });

  event.waitUntil(promiseChain);
});
*/

self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  const promiseChain = clients.matchAll({
    type: 'window',
    includeUncontrolled: true
  })
  .then((windowClients) => {
    client = windowClients[0];

    if (client) {
      return client.focus();
    } else {
      return clients.openWindow('/');
    }
  });

  event.waitUntil(promiseChain);
});

