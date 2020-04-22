self.addEventListener('push', async function(event) {
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

    // find the client(s) you want to send messages to and check if they are focused
    const promiseChain = clients.matchAll({
        includeUncontrolled: true,
        type: 'window'
    }).then((clients) => {
        let clientFocused = false;
        if (clients && clients.length) {
            const client = clients[0];
            client.postMessage({title: title, options: options});

            if(client.focused) {
                clientFocused = true;
            }
        }
        return clientFocused;
    })
    .then((clientFocused) => {
       if(clientFocused) {
           console.log("Don't need to show notification");
           return;
        }

        self.registration.showNotification(title, options);
    });
});

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

