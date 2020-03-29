self.addEventListener('push', async function(event) {
    console.log('[Service Worker] Push Received.');
    console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);

    var options = {
        icon:  '/ico/android-chrome-192x192.png',
        badge: '/ico/favicon-32x32.png'
    };

    try {
        data = event.data.json();
        console.log(data);
        title = data.title;

        options = Object.assign({}, data.options, options);
        console.log(options);
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

buerro_url = 'http://localhost:4000/'

self.addEventListener('notificationclick', function(event) {
  console.log('On notification click: ', event.notification.tag);
  event.notification.close();

  // This looks to see if the current is already open and
  // focuses if it is
  event.waitUntil(clients.matchAll({
    type: "window"
  }).then(function(clientList) {
    for (var i = 0; i < clientList.length; i++) {
      var client = clientList[i];
      if (client.url == buerro_url) {
        return client.focus(); // TODO doesnt seem to work
      }
    }
    if (clients.openWindow)
      return clients.openWindow('/');
  }));
});

