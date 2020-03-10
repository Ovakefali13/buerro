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

    $(".chatcontainer").append(generateChatBubble(true, "Hello its me the bot"));
    $(".chatcontainer").append(generateChatBubble(false, "Hello its me the user"));

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