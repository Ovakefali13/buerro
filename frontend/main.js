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


$(document).ready(function() {
    notify("Hello World", "This is a test notification", false);
})
